from django.db import models
from apps.accounts.models import CustomUser


class LeadershipPosition(models.Model):
    POSITIONS = [
        ('chairperson', 'Chairperson'),
        ('cell_leader', 'Cell Leader'),
        ('marketing_leader', 'Marketing Leader'),
        ('hospitality_leader', 'Hospitality Leader'),
        ('evangelism_leader', 'Evangelism Leader'),
        ('prayer_leader', 'Prayer Leader'),
        ('choir_leader', 'Choir Leader'),
    ]

    name = models.CharField(max_length=50, choices=POSITIONS, unique=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.get_name_display()


class LeadershipAssignment(models.Model):
    position = models.ForeignKey(LeadershipPosition, on_delete=models.CASCADE, related_name='assignments')
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leader_of')
    second_in_cmd = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='second_in_cmd_of'
    )
    year = models.IntegerField()
    date_assigned = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('position', 'year')
        ordering = ['position__sort_order']

    def __str__(self):
        return f"{self.position} — {self.leader.get_full_name()} ({self.year})"
