from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates all roles and the default admin user.'

    def handle(self, *args, **kwargs):
        # 1. Create all roles
        role_names = [Role.ADMIN, Role.PASTOR, Role.CELL_LEADER, Role.FACILITATOR, Role.LEADERSHIP]
        for name in role_names:
            Role.objects.get_or_create(name=name)
            self.stdout.write(f'  Role ready: {name}')

        # 2. Create leadership positions safely
        try:
            from apps.leadership.models import LeadershipPosition
            positions = [
                ('chairperson',        1),
                ('cell_leader',        2),
                ('marketing_leader',   3),
                ('hospitality_leader', 4),
                ('evangelism_leader',  5),
                ('prayer_leader',      6),
                ('choir_leader',       7),
            ]
            for name, order in positions:
                LeadershipPosition.objects.get_or_create(name=name, defaults={'sort_order': order})
                self.stdout.write(f'  Position ready: {name}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Skipping positions: {e}'))

        # 3. Create admin user
        admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)
        if User.objects.filter(username='admin').exists():
            user = User.objects.get(username='admin')
            user.set_password('1234')
            user.role = admin_role
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.WARNING('Admin password reset to 1234.'))
        else:
            User.objects.create_superuser(
                username='admin', password='1234',
                email='admin@campusignite.org',
                first_name='Admin', last_name='User',
                role=admin_role,
            )
            self.stdout.write(self.style.SUCCESS('Admin created: admin / 1234'))