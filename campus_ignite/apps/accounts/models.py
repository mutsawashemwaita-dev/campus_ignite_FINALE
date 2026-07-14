from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    PASTOR = 'pastor'
    CELL_LEADER = 'cell_leader'
    FACILITATOR = 'facilitator'
    LEADERSHIP = 'leadership'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (PASTOR, 'Pastor'),
        (CELL_LEADER, 'Cell Leader'),
        (FACILITATOR, 'Cell Facilitator'),
        (LEADERSHIP, 'Leadership Member'),
        (ADMIN, 'Administrator'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='users/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def has_role(self, *role_names):
        return self.role and self.role.name in role_names

    @property
    def is_pastor(self):
        return self.has_role(Role.PASTOR)

    @property
    def is_cell_leader(self):
        return self.has_role(Role.CELL_LEADER)

    @property
    def is_facilitator(self):
        return self.has_role(Role.FACILITATOR)

    @property
    def is_leadership(self):
        return self.has_role(Role.LEADERSHIP)

    @property
    def is_admin(self):
        return self.has_role(Role.ADMIN) or self.is_superuser
