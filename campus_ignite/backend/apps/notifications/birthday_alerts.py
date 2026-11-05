import datetime
from django.core.cache import cache
from apps.accounts.models import CustomUser
from apps.notifications.models import Notification


def send_birthday_notifications():
    today = datetime.date.today()
    cache_key = f"birthday_alerts_run_{today.isoformat()}"
    if cache.get(cache_key):
        return

    upcoming = []
    for person in CustomUser.objects.filter(is_active=True, birthday__isnull=False):
        bd = person.birthday
        try:
            this_year_bd = bd.replace(year=today.year)
        except ValueError:
            continue
        if this_year_bd < today:
            this_year_bd = bd.replace(year=today.year + 1)
        days_away = (this_year_bd - today).days
        if 0 <= days_away <= 7:
            upcoming.append((person, days_away))

    if not upcoming:
        cache.set(cache_key, True, 60 * 60 * 6)
        return

    recipients = list(CustomUser.objects.filter(
        is_active=True,
        role__name__in=['admin', 'pastor', 'cell_leader', 'leadership']
    ))

    # Pre-fetch existing birthday notifications created today to avoid N*M queries
    existing_today = set(
        Notification.objects.filter(
            created_at__date=today,
            source_type='birthday'
        ).values_list('recipient_id', 'title')
    )

    to_create = []
    for person, days_away in upcoming:
        if days_away == 0:
            title   = f"🎂 Birthday Today — {person.get_full_name()}!"
            message = f"{person.get_full_name()} is celebrating their birthday today!"
        elif days_away == 1:
            title   = f"🎂 Birthday Tomorrow — {person.get_full_name()}"
            message = f"{person.get_full_name()}'s birthday is tomorrow ({person.birthday.strftime('%d %B')})."
        else:
            title   = f"🎂 Upcoming Birthday — {person.get_full_name()}"
            message = f"{person.get_full_name()}'s birthday is in {days_away} days on {person.birthday.strftime('%d %B')}."

        for recipient in recipients:
            if (recipient.id, title) not in existing_today:
                to_create.append(
                    Notification(
                        recipient=recipient,
                        title=title,
                        message=message,
                        source_type='birthday',
                        source_id=person.pk,
                    )
                )

    if to_create:
        Notification.objects.bulk_create(to_create)

    # Cache for 6 hours so it doesn't re-run on subsequent page loads
    cache.set(cache_key, True, 60 * 60 * 6)