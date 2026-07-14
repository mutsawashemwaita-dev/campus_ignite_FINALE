from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import Pastor
from .forms import PastorForm


@login_required
def pastor_list(request):
    pastors = Pastor.objects.filter(is_active=True).select_related('user')
    return render(request, 'pastors/list.html', {'pastors': pastors})


@login_required
@role_required('admin', 'pastor')
def pastor_create(request):
    if request.method == 'POST':
        form = PastorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pastor added successfully.')
            return redirect('pastor_list')
    else:
        form = PastorForm()
    return render(request, 'pastors/form.html', {'form': form, 'title': 'Add Pastor'})


@login_required
@role_required('admin', 'pastor')
def pastor_update(request, pk):
    pastor = get_object_or_404(Pastor, pk=pk)
    if request.method == 'POST':
        form = PastorForm(request.POST, request.FILES, instance=pastor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pastor updated.')
            return redirect('pastor_list')
    else:
        form = PastorForm(instance=pastor)
    return render(request, 'pastors/form.html', {'form': form, 'title': 'Edit Pastor'})


@login_required
@role_required('admin')
def pastor_deactivate(request, pk):
    pastor = get_object_or_404(Pastor, pk=pk)
    pastor.is_active = False
    pastor.save()
    messages.success(request, f'{pastor} has been deactivated.')
    return redirect('pastor_list')
