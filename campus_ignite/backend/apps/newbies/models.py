from django.db import models
from apps.accounts.models import CustomUser


class Newbie(models.Model):
    YEAR_CHOICES = [
        ('Part 1', 'Part 1'),
        ('Part 2', 'Part 2'),
        ('Part 3', 'Part 3'),
        ('Part 4', 'Part 4'),
    ]

    STATUS_CHOICES = [
        ('new',       'New'),
        ('contacted', 'Contacted'),
        ('following', 'Following Up'),
        ('connected', 'Connected to Cell'),
    ]

    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    phone           = models.CharField(max_length=20)
    program         = models.CharField(max_length=200)
    year_of_study   = models.CharField(max_length=10, choices=YEAR_CHOICES, default='Part 1')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes           = models.TextField(blank=True)
    registered_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    date_registered = models.DateField(auto_now_add=True)

    class Meta:
        app_label = 'newbies'
        ordering = ['-date_registered']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"