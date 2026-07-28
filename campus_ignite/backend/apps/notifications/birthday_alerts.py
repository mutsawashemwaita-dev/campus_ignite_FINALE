import datetime
from apps.accounts.models import CustomUser
from apps.notifications.models import Notification


def send_birthday_notifications():
    today = datetime.date.today()
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
        return

    recipients = CustomUser.objects.filter(
        is_active=True,
        role__name__in=['admin', 'pastor', 'cell_leader', 'leadership']
    )

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
            already_notified = Notification.objects.filter(
                recipient=recipient,
                title=title,
                created_at__date=today
            ).exists()
            if not already_notified:
                Notification.objects.create(
                    recipient=recipient,
                    title=title,
                    message=message,
                    source_type='birthday',
                    source_id=person.pk,
                )