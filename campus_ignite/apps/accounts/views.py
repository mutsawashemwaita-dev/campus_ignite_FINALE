from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomLoginForm, ProfileUpdateForm


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'auth/login.html'


@login_required
def dashboard(request):
    from apps.cells.models import Cell, CellMeetingReport
    from apps.services.models import ServiceRecord
    from apps.notifications.models import Notification

    user = request.user

    my_cells = Cell.objects.none()
    if user.is_cell_leader or user.is_facilitator or user.is_admin:
        my_cells = (
            Cell.objects.filter(facilitator=user, is_active=True) |
            Cell.objects.filter(second_in_cmd=user, is_active=True)
        ).distinct().select_related('cell_type')

    context = {
        'total_cells': Cell.objects.filter(is_active=True).count(),
        'recent_service': ServiceRecord.objects.order_by('-date').first(),
        'unread_count': Notification.objects.filter(recipient=user, is_read=False).count(),
        'my_cells': my_cells,
        'recent_notifications': Notification.objects.filter(recipient=user).order_by('-created_at')[:5],
        'pending_reports': CellMeetingReport.objects.filter(
            cell__in=my_cells
        ).order_by('-date')[:5] if my_cells else [],
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'auth/profile.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
