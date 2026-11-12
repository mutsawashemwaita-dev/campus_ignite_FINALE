from django import forms
from apps.accounts.models import CustomUser
from .models import Cell, CellType, CellMember, CellMeetingReport, CellEvent, ConsolidatedCellReport


class CellForm(forms.Form):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    name = forms.CharField(
        label='Cell Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Zion Cell, Grace Cell'})
    )
    cell_type_name = forms.CharField(
        label='Cell Type',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Campus Cell, Ladies Cell', 'list': 'cell-type-list'})
    )
    venue = forms.CharField(
        label='Venue',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting venue (e.g. Room 4B, Library)'})
    )
    meeting_day = forms.CharField(
        label='Meeting Day',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monday, Wednesday', 'list': 'day-list'})
    )
    meeting_time = forms.TimeField(
        label='Meeting Time',
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    facilitator = forms.ModelChoiceField(
        label='Cell Facilitator',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select Facilitator --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    second_in_cmd = forms.ModelChoiceField(
        label='2IC (Second in Command)',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select 2IC (Optional) --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Hidden/legacy string fields for fallback & backwards-compatibility
    facilitator_username = forms.CharField(required=False, widget=forms.HiddenInput())
    second_in_cmd_username = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_qs = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['facilitator'].queryset = user_qs
        self.fields['second_in_cmd'].queryset = user_qs
        if 'initial' in kwargs:
            init = kwargs['initial']
            if 'facilitator_username' in init and not init.get('facilitator') and init['facilitator_username']:
                try:
                    self.initial['facilitator'] = CustomUser.objects.get(username=init['facilitator_username'])
                except CustomUser.DoesNotExist:
                    pass
            if 'second_in_cmd_username' in init and not init.get('second_in_cmd') and init['second_in_cmd_username']:
                try:
                    self.initial['second_in_cmd'] = CustomUser.objects.get(username=init['second_in_cmd_username'])
                except CustomUser.DoesNotExist:
                    pass

    def clean_cell_type_name(self):
        name = self.cleaned_data.get('cell_type_name', '').strip()
        if not name:
            raise forms.ValidationError('Please enter a cell type.')
        ct, _ = CellType.objects.get_or_create(name=name)
        return ct

    def clean(self):
        cleaned = super().clean()

        # Facilitator resolution
        facil = cleaned.get('facilitator')
        facil_un = self.data.get('facilitator_username', '').strip()
        if not facil and facil_un:
            try:
                facil = CustomUser.objects.get(username=facil_un)
                cleaned['facilitator'] = facil
            except CustomUser.DoesNotExist:
                self.add_error('facilitator', f'No user with username "{facil_un}".')
        elif not facil:
            self.add_error('facilitator', 'Please select a cell facilitator.')

        # 2IC resolution
        sec = cleaned.get('second_in_cmd')
        sec_un = self.data.get('second_in_cmd_username', '').strip()
        if not sec and sec_un:
            try:
                sec = CustomUser.objects.get(username=sec_un)
                cleaned['second_in_cmd'] = sec
            except CustomUser.DoesNotExist:
                self.add_error('second_in_cmd', f'No user with username "{sec_un}".')

        if facil and sec and facil == sec:
            self.add_error('second_in_cmd', 'The 2IC cannot be the same person as the facilitator.')

        # Maintain legacy keys in cleaned_data
        cleaned['facilitator_username'] = facil
        cleaned['second_in_cmd_username'] = sec
        return cleaned

    def save(self, instance=None):
        d = self.cleaned_data
        facil = d['facilitator']
        sec = d.get('second_in_cmd')
        if instance:
            instance.name = d['name']
            instance.cell_type = d['cell_type_name']
            instance.venue = d.get('venue', '')
            instance.meeting_day = d['meeting_day']
            instance.meeting_time = d['meeting_time']
            instance.facilitator = facil
            instance.second_in_cmd = sec
            instance.save()
            return instance
        return Cell.objects.create(
            name=d['name'],
            cell_type=d['cell_type_name'],
            venue=d.get('venue', ''),
            meeting_day=d['meeting_day'],
            meeting_time=d['meeting_time'],
            facilitator=facil,
            second_in_cmd=sec,
        )


class CellMemberForm(forms.Form):
    """Add an existing Member to a cell."""
    ATTENDANCE_CHOICES = [
        ('consistent', 'Consistent – attends every session'),
        ('regular',    'Regular – attends most sessions'),
        ('visitor',    'Visitor – occasional/new'),
    ]
    member_name = forms.CharField(
        label='Member Name or ID',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type name to search or leave blank to add new person first'}),
        required=False,
    )
    member_id = forms.IntegerField(
        widget=forms.HiddenInput(), required=False
    )
    attendance_type = forms.ChoiceField(
        label='Attendance Type',
        choices=ATTENDANCE_CHOICES,
        widget=forms.RadioSelect(),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes about this member...'})
    )


class CellMeetingReportForm(forms.ModelForm):
    facilitated_by = forms.ModelChoiceField(
        label='Facilitated By',
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label='-- Select Facilitator --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    facilitated_by_username = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CellMeetingReport
        fields = ['date', 'time_started', 'time_ended', 'head_count', 'summary', 'went_wrong', 'went_right', 'highlights']
        widgets = {
            'date':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_started': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_ended':   forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'head_count':   forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number present'}),
            'summary':      forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Summary of the meeting...'}),
            'went_wrong':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Challenges faced...'}),
            'went_right':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What went well...'}),
            'highlights':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key highlights...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['facilitated_by'].queryset = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        if 'initial' in kwargs:
            init = kwargs['initial']
            if 'facilitated_by_username' in init and not init.get('facilitated_by') and init['facilitated_by_username']:
                try:
                    self.initial['facilitated_by'] = CustomUser.objects.get(username=init['facilitated_by_username'])
                except CustomUser.DoesNotExist:
                    pass

    def clean(self):
        cleaned = super().clean()
        facil = cleaned.get('facilitated_by')
        un = self.data.get('facilitated_by_username', '').strip()
        if not facil and un:
            try:
                facil = CustomUser.objects.get(username=un)
                cleaned['facilitated_by'] = facil
            except CustomUser.DoesNotExist:
                self.add_error('facilitated_by', f'No user with username "{un}".')
        elif not facil:
            self.add_error('facilitated_by', 'Please select who facilitated the meeting.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.facilitated_by = self.cleaned_data['facilitated_by']
        if commit:
            instance.save()
        return instance


class CellEventForm(forms.ModelForm):
    class Meta:
        model = CellEvent
        fields = ['title', 'description', 'event_date', 'event_time']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Event description (optional)'}),
            'event_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'event_time':  forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class ConsolidatedReportForm(forms.ModelForm):
    class Meta:
        model = ConsolidatedCellReport
        fields = ['period_start', 'period_end', 'summary']
        widgets = {
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'summary':      forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Consolidated summary of all cell reports for this period...'}),
        }
