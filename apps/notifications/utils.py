from .models import Notification
from apps.accounts.models import CustomUser


def create_notification(recipient=None, recipient_id=None, title='', message='', source_type='', source_id=None):
    """Helper to create a notification for a user."""
    if recipient_id and not recipient:
        try:
            recipient = CustomUser.objects.get(pk=recipient_id)
        except CustomUser.DoesNotExist:
            return None
    if recipient:
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            source_type=source_type,
            source_id=source_id,
        )
