from django import forms
from .models import Department, DepartmentMember, DepartmentPost


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
        label='Member Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type the username of the person to add'})
    )
    role_in_dept = forms.CharField(
        label='Role in Department',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Soprano, Sound Engineer, Usher'})
    )

    def clean_member_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('member_username', '').strip()
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')


class DepartmentPostForm(forms.ModelForm):
    class Meta:
        model = DepartmentPost
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content':   forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your post, announcement or update...'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
