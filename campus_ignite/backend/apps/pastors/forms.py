from django import forms
from .models import Pastor


TITLE_CHOICES = [
    ('Senior Pastor', 'Senior Pastor'),
    ('Associate Pastor', 'Associate Pastor'),
    ('Assistant Pastor', 'Assistant Pastor'),
    ('Youth Pastor', 'Youth Pastor'),
    ('Campus Pastor', 'Campus Pastor'),
]


class PastorForm(forms.ModelForm):
    # Override user fields as plain text inputs
    user_username = forms.CharField(
        label='Username (existing user)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username of existing user'}),
        required=False,
        help_text='Type the username of the user to assign as pastor'
    )
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Pastor, Associate Pastor'}),
    )
    bio = forms.CharField(
        label='Biography',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short biography...'}),
    )
    date_appointed = forms.DateField(
        label='Date Appointed',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = Pastor
        fields = ['title', 'bio', 'date_appointed']

    def clean_user_username(self):
        from apps.accounts.models import CustomUser
        username = self.cleaned_data.get('user_username')
        if username:
            try:
                return CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError(f'No user found with username "{username}".')
        return None

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.cleaned_data.get('user_username')
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
