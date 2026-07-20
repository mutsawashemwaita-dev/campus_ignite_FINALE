from django.db import models
from apps.accounts.models import CustomUser


class Notification(models.Model):
    SOURCE_TYPES = [
        ('cell_event', 'Cell Event'),
        ('consolidated_report', 'Consolidated Report'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, blank=True)
    source_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.recipient.username}] {self.title}"
