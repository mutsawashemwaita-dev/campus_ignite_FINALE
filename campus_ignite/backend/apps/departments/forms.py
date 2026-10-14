from django import forms
from .models import Department, DepartmentMember, DepartmentPost, DepartmentEvent

class DepartmentEventForm(forms.ModelForm):
    class Meta:
        model  = DepartmentEvent
        fields = ['title', 'description', 'event_date', 'event_time']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Event description (optional)'}),
            'event_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'event_time':  forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class DepartmentForm(forms.Form):
    name = forms.CharField(
        label='Department Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Zion Choir, Media Team'})
    )
    dept_type = forms.CharField(
        label='Department Type',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'choir / hospitality / marketing / evangelism / prayer / ushering / media / welfare / youth / other'
        }),
        help_text='Enter one of: choir, hospitality, marketing, evangelism, prayer, ushering, media, welfare, youth, other'
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of this department...'})
    )
    leader_username = forms.CharField(
        label='Leader Username',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type the leader\'s username'})
    )
    second_in_cmd_username = forms.CharField(
        label='2IC Username',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type the 2IC\'s username (optional)'})
    )

    def clean_dept_type(self):
        val = self.cleaned_data.get('dept_type', '').strip().lower()
        valid = ['choir','hospitality','marketing','evangelism','prayer','ushering','media','welfare','youth','other']
        if val not in valid:
            raise forms.ValidationError(f'Choose from: {", ".join(valid)}')
        return val

    def clean_leader_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('leader_username', '').strip()
        if not username:
            return None
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')

    def clean_second_in_cmd_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('second_in_cmd_username', '').strip()
        if not username:
            return None
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')

    def save(self, instance=None):
        data = self.cleaned_data
        if instance:
            instance.name        = data['name']
            instance.dept_type   = data['dept_type']
            instance.description = data.get('description', '')
            instance.leader      = data['leader_username']
            instance.second_in_cmd = data['second_in_cmd_username']
            instance.save()
            return instance
        return Department.objects.create(
            name         = data['name'],
            dept_type    = data['dept_type'],
            description  = data.get('description', ''),
            leader       = data['leader_username'],
            second_in_cmd= data['second_in_cmd_username'],
        )


class DepartmentMemberForm(forms.Form):
    member_username = forms.CharField(
        label='Member Username or Full Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. johndoe or John Doe'})
    )
    role_in_dept = forms.CharField(
        label='Role in Department',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Soprano, Sound Engineer, Usher'})
    )

    def clean_member_username(self):
        from apps.accounts.models import CustomUser
        value = self.cleaned_data.get('member_username', '').strip()

        # Try an exact username match first
        try:
            return CustomUser.objects.get(username=value)
        except CustomUser.DoesNotExist:
            pass

        # Fall back to matching by full name (handles non-login members)
        matches = [u for u in CustomUser.objects.all() if u.get_full_name().strip().lower() == value.lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise forms.ValidationError(
                f'Multiple people are named "{value}". Please use their username instead to be specific.'
            )
        raise forms.ValidationError(f'No person found with username or name "{value}".')


class DepartmentPostForm(forms.ModelForm):
    class Meta:
        model = DepartmentPost
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content':   forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your post, announcement or update...'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


def manageable_departments(user):
    """Departments this user is allowed to manage."""
    from django.db.models import Q
    qs = Department.objects.filter(is_active=True)
    if user.is_admin or user.is_pastor or user.is_chairperson:
        return qs
    return qs.filter(
        Q(leader=user) | Q(second_in_cmd=user) | Q(members__user=user)
    ).distinct()


class DepartmentNewMemberForm(forms.Form):
    """Lets a leader create a brand-new non-login member. Adding them to a
    department is optional. Intentionally has NO username/password/role fields."""
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    phone = forms.CharField(
        label='Phone Number', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'})
    )
    email = forms.EmailField(
        label='Email Address', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address (optional)'})
    )
    birthday = forms.DateField(
        label='Birthday', required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    department = forms.ModelChoiceField(
        label='Add to a department? (optional)',
        queryset=Department.objects.none(),
        required=False,
        empty_label="No, just add them to the system",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    role_in_dept = forms.CharField(
        label='Role in Department (only if adding to one)', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Soprano, Sound Engineer, Usher'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['department'].queryset = manageable_departments(user)

    def clean(self):
        cleaned = super().clean()
        first = (cleaned.get('first_name') or '').strip()
        last = (cleaned.get('last_name') or '').strip()
        if first and last:
            from apps.accounts.models import CustomUser
            if CustomUser.objects.filter(first_name__iexact=first, last_name__iexact=last).exists():
                raise forms.ValidationError(
                    f'{first} {last} already exists in the system. To put them in a department, '
                    f'use "Add Member" on the department page and type their name. '
                    f'(If this is a different person with the same name, ask an admin to add them.)'
                )
        return cleaned

    def save(self):
        import uuid
        from apps.accounts.models import CustomUser
        data = self.cleaned_data
        user = CustomUser(
            username=f"member_{uuid.uuid4().hex[:8]}",
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            birthday=data.get('birthday'),
        )
        user.set_unusable_password()
        user.save()

        department = data.get('department')
        if department:
            DepartmentMember.objects.create(
                department=department,
                user=user,
                role_in_dept=data.get('role_in_dept', ''),
            )
        return user