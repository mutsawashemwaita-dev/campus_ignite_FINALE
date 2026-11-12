from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification


@login_required
def print_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'print/notifications.html', {'notifications': notifications})
