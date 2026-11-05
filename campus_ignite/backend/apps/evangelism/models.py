from django.db import models
from apps.accounts.models import CustomUser
from apps.cells.models import Cell


class EvangelismCampaign(models.Model):
    """One semester-long recruitment campaign (e.g. 'Kingdom Builders')."""
    name = models.CharField(max_length=100, default='Kingdom Builders')
    semester_label = models.CharField(max_length=100, help_text='e.g. Semester 2 · 2026')
    campus_goal = models.PositiveIntegerField(default=100, help_text='Total new members the campus aims for')
    prize_text = models.CharField(
        max_length=200, blank=True,
        default='The Cell with the most Recruits will be Granted a $100 Prize',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only one campaign is active at a time. Ticking this switches any other campaign off.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} – {self.semester_label}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            EvangelismCampaign.objects.exclude(pk=self.pk).update(is_active=False)


class CampaignCellGoal(models.Model):
    """How many new members a particular cell is aiming for in a campaign."""
    campaign = models.ForeignKey(EvangelismCampaign, on_delete=models.CASCADE, related_name='cell_goals')
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='evangelism_goals')
    target = models.PositiveIntegerField(help_text='e.g. 33')

    class Meta:
        unique_together = ('campaign', 'cell')
        ordering = ['cell__name']

    def __str__(self):
        return f"{self.cell.name}: {self.target}"


class Recruit(models.Model):
    INDEPENDENT = 'independent'
    REFERRAL = 'referral'
    CONSISTENT = 'consistent'
    CATEGORY_CHOICES = [
        (INDEPENDENT, 'Independent Member'),
        (REFERRAL, 'Referral Member'),
        (CONSISTENT, 'Consistent Member'),
    ]

    campaign = models.ForeignKey(EvangelismCampaign, on_delete=models.CASCADE, related_name='recruits')
    cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True, related_name='recruits')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=INDEPENDENT)
    full_name = models.CharField(max_length=200)
    referral_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30)
    program = models.CharField(max_length=150, blank=True)
    residency = models.CharField(max_length=150, blank=True)
    added_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='recruits_added'
    )
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added', '-id']

    def __str__(self):
        return f"{self.full_name} ({self.get_category_display()})"

    @property
    def counts_toward_goal(self):
        return self.category != self.CONSISTENT
