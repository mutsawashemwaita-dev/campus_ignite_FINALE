from django.db import models
from apps.accounts.models import CustomUser


class ServiceRecord(models.Model):
    date = models.DateField()
    preacher = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='preached_services'
    )
    guest_preacher = models.CharField(max_length=200, blank=True, help_text='Use if preacher is not a system user')
    message_title = models.CharField(max_length=300)
    message_summary = models.TextField()
    flow_of_service = models.TextField(help_text='Enter each part on a new line, e.g. Praise & Worship, Prayer, Announcements, Sermon...')
    head_count = models.IntegerField()
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recorded_services')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        preacher_name = self.guest_preacher or (self.preacher.get_full_name() if self.preacher else 'Unknown')
        return f"Service – {self.date} | {preacher_name}"

    def get_flow_list(self):
        return [line.strip() for line in self.flow_of_service.split('\n') if line.strip()]
