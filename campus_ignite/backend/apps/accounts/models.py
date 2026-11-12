from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class Role(models.Model):
    PASTOR      = 'pastor'
    CELL_LEADER = 'cell_leader'
    FACILITATOR = 'facilitator'
    LEADERSHIP  = 'leadership'
    CHAIRPERSON = 'chairperson'
    ADMIN       = 'admin'

    ROLE_CHOICES = [
        (PASTOR,      'Pastor'),
        (CELL_LEADER, 'Cell Leader'),
        (FACILITATOR, 'Cell Facilitator'),
        (LEADERSHIP,  'Leadership Member'),
        (CHAIRPERSON, 'Chairperson'),
        (ADMIN,       'Administrator'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class CustomUserManager(UserManager):
    def login_users(self):
        """Users who have login access and system credentials."""
        return self.filter(is_member_only=False).exclude(password__startswith='!')

    def member_attendees(self):
        """Congregants/attendees without system login access."""
        return self.filter(models.Q(is_member_only=True) | models.Q(password__startswith='!'))


class CustomUser(AbstractUser):
    role      = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_alumni = models.BooleanField(default=False)
    photo     = models.ImageField(upload_to='users/', null=True, blank=True)
    phone     = models.CharField(max_length=20, blank=True)
    bio       = models.TextField(blank=True)
    birthday  = models.DateField(null=True, blank=True)
    is_member_only = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Designates whether this person is an attendee/member without system credentials."
    )

    objects = CustomUserManager()

    def __str__(self):
        name = self.get_full_name().strip() or self.username
        role_label = self.role.get_name_display() if self.role else 'Member'
        return f"{name} ({role_label})"

    def save(self, *args, **kwargs):
        # Auto-sync is_member_only with unusable password / synthetic member_ usernames
        if not self.has_usable_password() and (self.username.startswith('member_') or not self.password):
            self.is_member_only = True
        super().save(*args, **kwargs)

    def set_as_member_only(self):
        """Revoke login access and mark as attendee/member."""
        self.is_member_only = True
        self.set_unusable_password()

    def set_as_login_user(self, password, username=None):
        """Grant login credentials and mark as login user."""
        self.is_member_only = False
        if username:
            self.username = username
        self.set_password(password)

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
    def is_chairperson(self):
        return self.has_role(Role.CHAIRPERSON)

    @property
    def is_admin(self):
        return self.has_role(Role.ADMIN) or self.is_superuser

    @property
    def can_login(self):
        return not self.is_member_only and self.has_usable_password()

    @property
    def birthday_display(self):
        if self.birthday:
            return self.birthday.strftime('%d %B')
        return None
