from django import forms
from .models import CustomUser, Role
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
            'placeholder': 'pastor / cell_leader / facilitator / leadership / admin'
        }),
        help_text='Leave blank for regular members'
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
        valid_roles = [Role.ADMIN, Role.PASTOR, Role.CELL_LEADER, Role.FACILITATOR, Role.LEADERSHIP]
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

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthday']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'birthday':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.role:
            self.fields['role_name'].initial = self.instance.role.name

    def clean_role_name(self):
        role_name = self.cleaned_data.get('role_name', '').strip().lower()
        if not role_name:
            return ''
        valid_roles = [Role.ADMIN, Role.PASTOR, Role.CELL_LEADER, Role.FACILITATOR, Role.LEADERSHIP]
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
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthday', 'bio', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'birthday':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio':        forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }
