from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates the default admin user (username: admin, password: 1234) and all roles.'

    def handle(self, *args, **kwargs):
        # Create all roles
        role_names = [
            Role.ADMIN, Role.PASTOR, Role.CELL_LEADER,
            Role.FACILITATOR, Role.LEADERSHIP,
        ]
        for name in role_names:
            Role.objects.get_or_create(name=name)
            self.stdout.write(f'  Role ready: {name}')

        admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)

        # Create or update the admin user
        if User.objects.filter(username='admin').exists():
            user = User.objects.get(username='admin')
            user.set_password('1234')
            user.role = admin_role
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.WARNING('Admin user already existed — password reset to 1234.'))
        else:
            User.objects.create_superuser(
                username='admin',
                password='1234',
                email='admin@campusignite.org',
                first_name='Admin',
                last_name='User',
                role=admin_role,
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: username=admin  password=1234'))

        self.stdout.write(self.style.SUCCESS('\nSetup complete. You can now log in at /auth/login/'))
