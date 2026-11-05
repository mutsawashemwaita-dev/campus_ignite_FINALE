import re
from django import forms
from apps.cells.models import Cell
from .models import Recruit


def _digits(value):
    return re.sub(r'\D', '', value or '')


class RecruitForm(forms.ModelForm):
    class Meta:
        model = Recruit
        fields = ['cell', 'category', 'full_name', 'referral_name', 'phone', 'program', 'residency']
        labels = {
            'cell': 'Cell',
            'category': 'Member type',
            'full_name': 'Full name',
            'referral_name': 'Referral full name',
            'phone': 'Phone',
            'program': 'Program',
            'residency': 'Residency',
        }
        widgets = {
            'cell': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'referral_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Who referred them? (optional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0771234567'}),
            'program': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mechanical Engineering'}),
            'residency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. On-Campus'}),
        }

    def __init__(self, *args, campaign=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = campaign
        if campaign is not None:
            self.fields['cell'].queryset = Cell.objects.filter(
                evangelism_goals__campaign=campaign
            ).distinct().order_by('name')
        self.fields['cell'].empty_label = 'Choose a cell'

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get('full_name') or '').strip()
        phone = cleaned.get('phone') or ''
        if self.campaign is not None and name and phone:
            for existing in Recruit.objects.filter(campaign=self.campaign, full_name__iexact=name):
                if _digits(existing.phone) == _digits(phone):
                    raise forms.ValidationError(
                        f'{name} is already saved as a {existing.get_category_display()}.'
                    )
        return cleaned
