from django.db import models
from apps.accounts.models import CustomUser


class Department(models.Model):
    DEPT_CHOICES = [
        ('choir',        'Choir'),
        ('hospitality',  'Hospitality'),
        ('marketing',    'Marketing'),
        ('evangelism',   'Evangelism'),
        ('prayer',       'Prayer'),
        ('ushering',     'Ushering'),
        ('media',        'Media & Tech'),
        ('welfare',      'Welfare'),
        ('youth',        'Youth'),
        ('other',        'Other'),
    ]

    name       = models.CharField(max_length=100)
    dept_type  = models.CharField(max_length=30, choices=DEPT_CHOICES, default='other')
    description= models.TextField(blank=True)
    leader     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='dept_leader_of')
    second_in_cmd = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='dept_2ic_of')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['dept_type', 'name']

    def __str__(self):
        return self.name


class DepartmentMember(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dept_memberships')
    role_in_dept = models.CharField(max_length=100, blank=True, help_text='e.g. Soprano, Sound Engineer')
    date_joined  = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('department', 'user')

    def __str__(self):
        return f"{self.user.get_full_name()} – {self.department.name}"


class DepartmentPost(models.Model):
    department  = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='posts')
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    posted_by   = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_pinned   = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.department.name} – {self.title}"
