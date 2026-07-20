from django import forms
from .models import Cell, CellMember, CellMeetingReport, CellEvent, ConsolidatedCellReport



class CellForm(forms.Form):
    name                   = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Zion Cell'}))
    cell_type_name         = forms.CharField(label='Cell Type', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Campus Cell, Ladies Cell'}))
    venue                  = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Meeting venue'}))
    meeting_day            = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Monday, Wednesday'}))
    meeting_time           = forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control','type':'time'}))
    facilitator_username   = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Facilitator username'}))
    second_in_cmd_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'2IC username (optional)'}))

    def clean_facilitator_username(self):
        from apps.accounts.models import CustomUser
        un = self.cleaned_data.get('facilitator_username','').strip()
        try: return CustomUser.objects.get(username=un)
        except CustomUser.DoesNotExist: raise forms.ValidationError(f'No user with username "{un}".')

    def clean_second_in_cmd_username(self):
        from apps.accounts.models import CustomUser
        un = self.cleaned_data.get('second_in_cmd_username','').strip()
        if not un: return None
        try: return CustomUser.objects.get(username=un)
        except CustomUser.DoesNotExist: raise forms.ValidationError(f'No user with username "{un}".')

    def clean_cell_type_name(self):
        from .models import CellType
        name = self.cleaned_data.get('cell_type_name','').strip()
        ct, _ = CellType.objects.get_or_create(name=name)
        return ct

    def save(self, instance=None):
        d = self.cleaned_data
        if instance:
            instance.name         = d['name']
            instance.cell_type    = d['cell_type_name']
            instance.venue        = d.get('venue','')
            instance.meeting_day  = d['meeting_day']
            instance.meeting_time = d['meeting_time']
            instance.facilitator  = d['facilitator_username']
            instance.second_in_cmd= d['second_in_cmd_username']
            instance.save()
            return instance
        return Cell.objects.create(
            name=d['name'], cell_type=d['cell_type_name'],
            venue=d.get('venue',''), meeting_day=d['meeting_day'],
            meeting_time=d['meeting_time'], facilitator=d['facilitator_username'],
            second_in_cmd=d['second_in_cmd_username'],
        )


class CellMemberForm(forms.Form):
    """Add an existing Member to a cell."""
    ATTENDANCE_CHOICES = [
        ('consistent','Consistent – attends every session'),
        ('regular',   'Regular – attends most sessions'),
        ('visitor',   'Visitor – occasional/new'),
    ]
    member_name = forms.CharField(
        label='Member Name or ID',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Type name to search or leave blank to add new person first'}),
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
        widget=forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Optional notes about this member...'})
    )


class CellMeetingReportForm(forms.ModelForm):
    facilitated_by_username = forms.CharField(
        label='Facilitated By (Username)',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username of who facilitated'})
    )
    class Meta:
        model  = CellMeetingReport
        fields = ['date','time_started','time_ended','head_count','summary','went_wrong','went_right','highlights']
        widgets = {
            'date':         forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'time_started': forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'time_ended':   forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'head_count':   forms.NumberInput(attrs={'class':'form-control','placeholder':'Number present'}),
            'summary':      forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Summary of the meeting...'}),
            'went_wrong':   forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Challenges faced...'}),
            'went_right':   forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'What went well...'}),
            'highlights':   forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Key highlights...'}),
        }
    def clean_facilitated_by_username(self):
        from apps.accounts.models import CustomUser
        un = self.cleaned_data.get('facilitated_by_username','').strip()
        try: return CustomUser.objects.get(username=un)
        except CustomUser.DoesNotExist: raise forms.ValidationError(f'No user with username "{un}".')
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.facilitated_by = self.cleaned_data['facilitated_by_username']
        if commit: instance.save()
        return instance


class CellEventForm(forms.ModelForm):
    class Meta:
        model  = CellEvent
        fields = ['title','description','event_date','event_time']
        widgets = {
            'title':       forms.TextInput(attrs={'class':'form-control','placeholder':'Event title'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Event description (optional)'}),
            'event_date':  forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'event_time':  forms.TimeInput(attrs={'class':'form-control','type':'time'}),
        }


class ConsolidatedReportForm(forms.Form):
    period_start    = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    period_end      = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    cell_names      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Cell A, Cell B, Cell C'}))
    summary         = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':5,'placeholder':'Overall summary...'}))
    total_headcount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    highlights      = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Key highlights...'}))
    challenges      = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Challenges faced...'}))
