from django import forms
from .models import ServiceRecord


class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = ['date', 'preacher', 'guest_preacher', 'message_title',
                  'message_summary', 'flow_of_service', 'head_count']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preacher': forms.Select(attrs={'class': 'form-select'}),
            'guest_preacher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if preacher is in the system'}),
            'message_title': forms.TextInput(attrs={'class': 'form-control'}),
            'message_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'flow_of_service': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 6,
                'placeholder': 'Praise & Worship\nOpening Prayer\nAnnouncements\nOffering\nSermon\nAltar Call\nBenediction'
            }),
            'head_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }
