from django import forms
from .models import Pastor


class PastorForm(forms.ModelForm):
    class Meta:
        model = Pastor
        fields = ['user', 'title', 'bio', 'date_appointed']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_appointed': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
