from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Role


class Command(BaseCommand):
    help = 'Creates the default Campus Ignite admin user (username: admin, password: 1234)'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Ensure the Admin role exists
        admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)

        # Create all default roles
        for role_name, _ in Role.ROLE_CHOICES:
            Role.objects.get_or_create(name=role_name)
        self.stdout.write('  Roles created.')

        # Create or update the admin user
        if User.objects.filter(username='admin').exists():
            user = User.objects.get(username='admin')
            user.set_password('1234')
            user.role = admin_role
            user.is_superuser = True
            user.is_staff = True
            user.first_name = 'Campus'
            user.last_name = 'Admin'
            user.save()
            self.stdout.write(self.style.WARNING('  Admin user already existed — password reset to 1234.'))
        else:
            User.objects.create_superuser(
                username='admin',
                password='1234',
                email='admin@campusignite.org',
                first_name='Campus',
                last_name='Admin',
                role=admin_role,
            )
            self.stdout.write(self.style.SUCCESS('  Admin user created.'))

        self.stdout.write(self.style.SUCCESS(
            '\n✔  Default admin ready.\n'
            '   Username : admin\n'
            '   Password : 1234\n'
            '   URL      : http://127.0.0.1:8000/auth/login/\n'
        ))
