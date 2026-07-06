from django import forms
from .models import ServiceRecord


class ServiceRecordForm(forms.ModelForm):
    preacher_username = forms.CharField(
        label='Preacher Username',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type username if preacher is in the system'
        }),
        help_text='Leave blank if using Guest Preacher name below'
    )

    class Meta:
        model = ServiceRecord
        fields = ['date', 'guest_preacher', 'message_title',
                  'message_summary', 'flow_of_service', 'head_count']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'guest_preacher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of guest/external preacher'
            }),
            'message_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title of the message preached'
            }),
            'message_summary': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Brief summary of what was preached...'
            }),
            'flow_of_service': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 7,
                'placeholder': (
                    'Enter each part of the service on a new line:\n'
                    'Praise & Worship\n'
                    'Opening Prayer\n'
                    'Announcements\n'
                    'Offering\n'
                    'Sermon\n'
                    'Altar Call\n'
                    'Benediction'
                )
            }),
            'head_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total number of people in attendance'
            }),
        }

    def clean_preacher_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('preacher_username')
        if not username:
            return None
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')

    def save(self, commit=True):
        instance = super().save(commit=False)
        preacher = self.cleaned_data.get('preacher_username')
        if preacher:
            instance.preacher = preacher
        if commit:
            instance.save()
        return instance
