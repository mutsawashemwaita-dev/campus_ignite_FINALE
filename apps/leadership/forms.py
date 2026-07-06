from django import forms
from .models import LeadershipAssignment


class LeadershipAssignmentForm(forms.Form):
    leader_username = forms.CharField(
        label='Leader Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type the username of the leader'
        }),
    )
    second_in_cmd_username = forms.CharField(
        label='2IC Username',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type the username of the 2nd in command (optional)'
        }),
    )
    year = forms.IntegerField(
        label='Year',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 2026'
        }),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active Assignment'
    )

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment:
            self.fields['leader_username'].initial = assignment.leader.username
            if assignment.second_in_cmd:
                self.fields['second_in_cmd_username'].initial = assignment.second_in_cmd.username
            self.fields['year'].initial = assignment.year
            self.fields['is_active'].initial = assignment.is_active

    def clean_leader_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('leader_username')
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')

    def clean_second_in_cmd_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('second_in_cmd_username')
        if not username:
            return None
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')
