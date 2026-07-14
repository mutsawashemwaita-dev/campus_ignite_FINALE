from django import forms
from .models import Cell, CellMeetingReport, CellEvent, ConsolidatedCellReport


class CellForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['name', 'cell_type', 'facilitator', 'second_in_cmd', 'venue', 'meeting_day', 'meeting_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cell_type': forms.Select(attrs={'class': 'form-select'}),
            'facilitator': forms.Select(attrs={'class': 'form-select'}),
            'second_in_cmd': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_day': forms.Select(attrs={'class': 'form-select'}),
            'meeting_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class CellMeetingReportForm(forms.ModelForm):
    class Meta:
        model = CellMeetingReport
        fields = ['date', 'time_started', 'time_ended', 'head_count',
                  'facilitated_by', 'summary', 'went_wrong', 'went_right', 'highlights']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_started': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_ended': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'head_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'facilitated_by': forms.Select(attrs={'class': 'form-select'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief summary of the cell meeting...'}),
            'went_wrong': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What challenges did you face?'}),
            'went_right': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What went well?'}),
            'highlights': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key highlights and testimonies...'}),
        }


class CellEventForm(forms.ModelForm):
    class Meta:
        model = CellEvent
        fields = ['title', 'description', 'event_date', 'event_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'event_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class ConsolidatedReportForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show cells this user facilitates or is 2IC of
            self.fields['cells_included'].queryset = (
                Cell.objects.filter(facilitator=user, is_active=True) |
                Cell.objects.filter(second_in_cmd=user, is_active=True)
            ).distinct()

    class Meta:
        model = ConsolidatedCellReport
        fields = ['period_start', 'period_end', 'summary', 'cells_included', 'reports_included']
        widgets = {
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'cells_included': forms.CheckboxSelectMultiple(),
            'reports_included': forms.CheckboxSelectMultiple(),
        }
