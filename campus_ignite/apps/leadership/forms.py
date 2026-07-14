from django import forms
from .models import LeadershipAssignment
from apps.accounts.models import CustomUser


class LeadershipAssignmentForm(forms.ModelForm):
    leader = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    second_in_cmd = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='2nd in Command (2IC)'
    )

    class Meta:
        model = LeadershipAssignment
        fields = ['leader', 'second_in_cmd', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
