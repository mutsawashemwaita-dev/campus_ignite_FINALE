from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser


class CellType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Cell(models.Model):
    DAYS = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
    ]

    name = models.CharField(max_length=100)
    cell_type = models.ForeignKey(CellType, on_delete=models.SET_NULL, null=True)
    facilitator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='facilitates')
    second_in_cmd = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='second_in_cmd_cell'
    )
    venue = models.CharField(max_length=200, blank=True)
    meeting_day = models.CharField(max_length=10, choices=DAYS)
    meeting_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_leader_ids(self):
        ids = [self.facilitator_id]
        if self.second_in_cmd_id:
            ids.append(self.second_in_cmd_id)
        return ids


class CellMeetingReport(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='reports')
    date = models.DateField()
    time_started = models.TimeField()
    time_ended = models.TimeField()
    head_count = models.IntegerField()
    facilitated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='facilitated_reports')
    summary = models.TextField()
    went_wrong = models.TextField(blank=True)
    went_right = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_reports')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.cell.name} – {self.date}"


class CellEvent(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return f"{self.title} ({self.cell.name} – {self.event_date})"


class ConsolidatedCellReport(models.Model):
    prepared_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    summary = models.TextField()
    cells_included = models.ManyToManyField(Cell, blank=True)
    reports_included = models.ManyToManyField(CellMeetingReport, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    sent_to_pastors = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Consolidated Report – {self.period_start} to {self.period_end}"
