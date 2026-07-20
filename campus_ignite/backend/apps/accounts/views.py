from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CustomLoginForm, AddPersonForm, EditPersonForm, ProfileUpdateForm
from .models import CustomUser, Role
from .decorators import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})


@login_required
def dashboard(request):
    from apps.cells.models import Cell, CellMeetingReport
    from apps.services.models import ServiceRecord
    from apps.notifications.models import Notification

    user = request.user
    my_cells = (
        Cell.objects.filter(facilitator=user, is_active=True) |
        Cell.objects.filter(second_in_cmd=user, is_active=True)
    ).distinct().select_related('cell_type')

    context = {
        'total_cells': Cell.objects.filter(is_active=True).count(),
        'total_users': CustomUser.objects.filter(is_active=True).count(),
        'recent_service': ServiceRecord.objects.order_by('-date').first(),
        'unread_count': Notification.objects.filter(recipient=user, is_read=False).count(),
        'my_cells': my_cells,
        'recent_notifications': Notification.objects.filter(recipient=user).order_by('-created_at')[:5],
        'pending_reports': CellMeetingReport.objects.filter(
            cell__in=my_cells).order_by('-date')[:5] if my_cells else [],
    }
    return render(request, 'dashboard.html', context)


@login_required
def user_list(request):
    users = CustomUser.objects.select_related('role').order_by('first_name', 'last_name')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_create(request):
    if request.method == 'POST':
        form = AddPersonForm(request.POST)
        if form.is_valid():
            user = form.save()
            label = f'"{user.get_full_name()}"'
            if user.has_usable_password():
                messages.success(request, f'{label} added. They can log in with username: {user.username}')
            else:
                messages.success(request, f'{label} added as a member (no login required).')
            return redirect('user_list')
    else:
        form = AddPersonForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add Person'})


@login_required
def user_edit(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = EditPersonForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{user_obj.get_full_name()}" updated.')
            return redirect('user_list')
    else:
        form = EditPersonForm(instance=user_obj)
    return render(request, 'accounts/user_form.html', {
        'form': form, 'title': f'Edit: {user_obj.get_full_name()}', 'edit': True, 'user_obj': user_obj
    })


@login_required
def user_deactivate(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if user_obj == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_list')
    user_obj.is_active = False
    user_obj.save()
    messages.success(request, f'"{user_obj.get_full_name()}" deactivated.')
    return redirect('user_list')


@login_required
def user_activate(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    user_obj.is_active = True
    user_obj.save()
    messages.success(request, f'"{user_obj.get_full_name()}" reactivated.')
    return redirect('user_list')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'auth/profile.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
