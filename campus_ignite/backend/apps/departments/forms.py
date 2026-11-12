from django import forms
from apps.accounts.models import CustomUser
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
    dept_type = forms.ChoiceField(
        label='Department Type',
        choices=Department.DEPT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of this department...'})
    )
    leader = forms.ModelChoiceField(
        label='Department Leader',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select Leader (Optional) --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    second_in_cmd = forms.ModelChoiceField(
        label='First 2IC',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select First 2IC (Optional) --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    second_in_cmd_2 = forms.ModelChoiceField(
        label='Second 2IC',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select Second 2IC (Optional) --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Hidden/legacy string fields for fallback & backwards-compatibility
    leader_username = forms.CharField(required=False, widget=forms.HiddenInput())
    second_in_cmd_username = forms.CharField(required=False, widget=forms.HiddenInput())
    second_in_cmd_2_username = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_qs = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['leader'].queryset = user_qs
        self.fields['second_in_cmd'].queryset = user_qs
        self.fields['second_in_cmd_2'].queryset = user_qs
        if 'initial' in kwargs:
            init = kwargs['initial']
            for field, legacy in [('leader', 'leader_username'), ('second_in_cmd', 'second_in_cmd_username'), ('second_in_cmd_2', 'second_in_cmd_2_username')]:
                if legacy in init and not init.get(field) and init[legacy]:
                    try:
                        self.initial[field] = CustomUser.objects.get(username=init[legacy])
                    except CustomUser.DoesNotExist:
                        pass

    def clean(self):
        cleaned = super().clean()

        # Resolve leader
        leader = cleaned.get('leader')
        leader_un = self.data.get('leader_username', '').strip()
        if not leader and leader_un:
            try:
                leader = CustomUser.objects.get(username=leader_un)
                cleaned['leader'] = leader
            except CustomUser.DoesNotExist:
                self.add_error('leader', f'No user found with username "{leader_un}".')

        # Resolve second_in_cmd
        ic1 = cleaned.get('second_in_cmd')
        ic1_un = self.data.get('second_in_cmd_username', '').strip()
        if not ic1 and ic1_un:
            try:
                ic1 = CustomUser.objects.get(username=ic1_un)
                cleaned['second_in_cmd'] = ic1
            except CustomUser.DoesNotExist:
                self.add_error('second_in_cmd', f'No user found with username "{ic1_un}".')

        # Resolve second_in_cmd_2
        ic2 = cleaned.get('second_in_cmd_2')
        ic2_un = self.data.get('second_in_cmd_2_username', '').strip()
        if not ic2 and ic2_un:
            try:
                ic2 = CustomUser.objects.get(username=ic2_un)
                cleaned['second_in_cmd_2'] = ic2
            except CustomUser.DoesNotExist:
                self.add_error('second_in_cmd_2', f'No user found with username "{ic2_un}".')

        if ic1 and ic2 and ic1 == ic2:
            self.add_error('second_in_cmd_2', 'The two 2ICs must be two different people.')
        if leader and ic1 and leader == ic1:
            self.add_error('second_in_cmd', 'The leader cannot also be the 2IC.')
        if leader and ic2 and leader == ic2:
            self.add_error('second_in_cmd_2', 'The leader cannot also be the second 2IC.')

        # Populate legacy username fields in cleaned_data
        cleaned['leader_username'] = leader
        cleaned['second_in_cmd_username'] = ic1
        cleaned['second_in_cmd_2_username'] = ic2
        return cleaned

    def save(self, instance=None):
        data = self.cleaned_data
        leader = data.get('leader')
        ic1 = data.get('second_in_cmd')
        ic2 = data.get('second_in_cmd_2')
        if instance:
            instance.name = data['name']
            instance.dept_type = data['dept_type']
            instance.description = data.get('description', '')
            instance.leader = leader
            instance.second_in_cmd = ic1
            instance.second_in_cmd_2 = ic2
            instance.save()
            return instance
        return Department.objects.create(
            name=data['name'],
            dept_type=data['dept_type'],
            description=data.get('description', ''),
            leader=leader,
            second_in_cmd=ic1,
            second_in_cmd_2=ic2,
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
        from django.db.models import Q
        value = self.cleaned_data.get('member_username', '').strip()

        # Try an exact username match first
        try:
            return CustomUser.objects.get(username=value)
        except CustomUser.DoesNotExist:
            pass

        # Fall back to matching by full name in DB (handles non-login members)
        parts = value.split()
        if len(parts) >= 2:
            matches = list(CustomUser.objects.filter(
                first_name__iexact=parts[0],
                last_name__iexact=' '.join(parts[1:])
            ))
        else:
            matches = list(CustomUser.objects.filter(
                Q(first_name__iexact=value) | Q(last_name__iexact=value)
            ))

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
        Q(leader=user) | Q(second_in_cmd=user) | Q(second_in_cmd_2=user) | Q(members__user=user)
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
            is_member_only=True,
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
 