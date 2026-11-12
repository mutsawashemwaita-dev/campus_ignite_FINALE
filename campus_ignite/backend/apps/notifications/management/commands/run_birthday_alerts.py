from django.core.management.base import BaseCommand
from django.core.cache import cache
import datetime
from apps.notifications.birthday_alerts import send_birthday_notifications


class Command(BaseCommand):
    help = 'Run daily automated upcoming birthday checks and send notifications to leaders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bypass the daily cache guard and force check immediately',
        )

    def handle(self, *args, **options):
        if options['force']:
            today = datetime.date.today()
            cache.delete(f"birthday_alerts_run_{today.isoformat()}")
            self.stdout.write(self.style.WARNING("Force flag supplied: cleared today's birthday cache guard."))

        self.stdout.write("Checking for upcoming birthdays...")
        send_birthday_notifications()
        self.stdout.write(self.style.SUCCESS("Successfully processed birthday notifications."))
