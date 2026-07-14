from django.db import models
from apps.accounts.models import CustomUser


class Pastor(models.Model):
    TITLE_CHOICES = [
        ('Senior Pastor', 'Senior Pastor'),
        ('Associate Pastor', 'Associate Pastor'),
        ('Assistant Pastor', 'Assistant Pastor'),
        ('Youth Pastor', 'Youth Pastor'),
        ('Campus Pastor', 'Campus Pastor'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pastor_profile')
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    bio = models.TextField(blank=True)
    date_appointed = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title', 'user__first_name']

    def __str__(self):
        return f"{self.title} {self.user.get_full_name()}"
