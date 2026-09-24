from django import forms
from .models import CustomUser, Role
from apps.departments.models import Department, DepartmentMember
import uuid


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

    def clean(self):
        from django.contrib.auth import authenticate
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            self.user = authenticate(username=username, password=password)
            if not self.user:
                raise forms.ValidationError('Invalid username or password.')
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class SignupForm(forms.Form):
    """Public self-registration. Every signup links the new account to exactly one
    department as a regular member — it does NOT grant leadership permissions."""
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        label='Email Address', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address (optional)'})
    )
    phone = forms.CharField(
        label='Phone Number', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'})
    )
    department = forms.ModelChoiceField(
        label='Department',
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='You will only be able to manage this department.'
    )
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Choose a password'})
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Username "{username}" is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', '')
        confirm  = cleaned_data.get('confirm_password', '')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        leadership_role, _ = Role.objects.get_or_create(name=Role.LEADERSHIP)
        user = CustomUser.objects.create_user(
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            role=leadership_role,
        )
        DepartmentMember.objects.get_or_create(
            department=data['department'],
            user=user,
            defaults={'role_in_dept': 'Leader'},
        )
        return user


class AddPersonForm(forms.Form):
    """Add any person - login/role is optional for regular members."""
    # Personal details
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        label='Email Address', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address (optional)'})
    )
    phone = forms.CharField(
        label='Phone Number', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'})
    )
    birthday = forms.DateField(
        label='Birthday', required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text='Used to display in Hospitality birthday section'
    )

    # Login & Role - OPTIONAL
    username = forms.CharField(
        label='Username', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. john_doe – only needed for leaders/staff'
        }),
        help_text='Leave blank for regular members who do not need to log in'
    )
    role_name = forms.CharField(
        label='Role', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'pastor / cell_leader / facilitator / leadership / admin / chairperson'
        }),
        help_text='Leave blank for regular members'
    )
    is_alumni = forms.BooleanField(
        label='Mark as Alumni', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_student_anchor = forms.BooleanField(
        label='Mark as Student Anchor', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    password = forms.CharField(
        label='Password', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Only needed if they will log in'}),
    )
    confirm_password = forms.CharField(
        label='Confirm Password', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Username "{username}" is already taken.')
        return username

    def clean_role_name(self):
        role_name = self.cleaned_data.get('role_name', '').strip().lower()
        if not role_name:
            return ''
        valid_roles = [Role.ADMIN, Role.PASTOR, Role.CELL_LEADER, Role.FACILITATOR, Role.LEADERSHIP, Role.CHAIRPERSON]
        if role_name not in valid_roles:
            raise forms.ValidationError(f'Invalid role. Choose from: {", ".join(valid_roles)}')
        return role_name

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', '').strip()
        password = cleaned_data.get('password', '').strip()
        confirm  = cleaned_data.get('confirm_password', '').strip()

        # If username provided, password required
        if username and not password:
            raise forms.ValidationError('Password is required when a username is provided.')
        if password and password != confirm:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self):
        data     = self.cleaned_data
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role_name= data.get('role_name', '').strip()

        # Generate a unique username for member-only records
        if not username:
            username = f"member_{uuid.uuid4().hex[:8]}"

        role = None
        if role_name:
            role, _ = Role.objects.get_or_create(name=role_name)

        if password:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                birthday=data.get('birthday'),
                role=role,
            )
        else:
            # Member only — no login
            user = CustomUser(
                username=username,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                birthday=data.get('birthday'),
                role=role,
            )
            user.set_unusable_password()
            user.save()

        if data.get('is_alumni'):
            user.is_alumni = True
            user.save()

        if data.get('is_student_anchor'):
            from apps.leadership.models import StudentAnchor
            StudentAnchor.objects.get_or_create(user=user, defaults={'is_active': True})

        return user


class EditPersonForm(forms.ModelForm):
    role_name = forms.CharField(
        label='Role', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'pastor / cell_leader / facilitator / leadership / admin (leave blank for member)'
        })
    )
    new_password = forms.CharField(
        label='New Password', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current'})
    )
    is_student_anchor = forms.BooleanField(
        label='Mark as Student Anchor', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthday', 'is_alumni']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'birthday':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_alumni':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.role:
            self.fields['role_name'].initial = self.instance.role.name
        if self.instance and self.instance.pk:
            from apps.leadership.models import StudentAnchor
            self.fields['is_student_anchor'].initial = StudentAnchor.objects.filter(
                user=self.instance, is_active=True
            ).exists()

    def clean_role_name(self):
        role_name = self.cleaned_data.get('role_name', '').strip().lower()
        if not role_name:
            return ''
        valid_roles = [Role.ADMIN, Role.PASTOR, Role.CELL_LEADER, Role.FACILITATOR, Role.LEADERSHIP, Role.CHAIRPERSON]
        if role_name not in valid_roles:
            raise forms.ValidationError(f'Choose from: {", ".join(valid_roles)}')
        return role_name

    def save(self, commit=True):
        user = super().save(commit=False)
        role_name = self.cleaned_data.get('role_name', '').strip()
        if role_name:
            role, _ = Role.objects.get_or_create(name=role_name)
            user.role = role
        else:
            user.role = None
        new_pw = self.cleaned_data.get('new_password', '').strip()
        if new_pw:
            user.set_password(new_pw)
        if commit:
            user.save()

            from apps.leadership.models import StudentAnchor
            wants_anchor = self.cleaned_data.get('is_student_anchor')
            existing = StudentAnchor.objects.filter(user=user, is_active=True).first()
            if wants_anchor and not existing:
                StudentAnchor.objects.get_or_create(user=user, defaults={'is_active': True})
            elif not wants_anchor and existing:
                existing.delete()
        return user


class ProfileUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        label='New Password', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
        help_text='Leave blank if you don\'t want to change your password'
    )
    confirm_password = forms.CharField(
        label='Confirm New Password', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat new password'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'birthday', 'bio', 'photo']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'birthday':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio':        forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('New passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
