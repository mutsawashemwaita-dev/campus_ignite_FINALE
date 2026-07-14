from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import ServiceRecord
from .forms import ServiceRecordForm


@login_required
def service_list(request):
    services = ServiceRecord.objects.select_related('preacher', 'recorded_by').all()
    return render(request, 'services/list.html', {'services': services})


@login_required
def service_detail(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    return render(request, 'services/detail.html', {'service': service})


@login_required
@role_required('admin', 'pastor', 'leadership')
def service_create(request):
    if request.method == 'POST':
        form = ServiceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, 'Service record saved.')
            return redirect('service_list')
    else:
        form = ServiceRecordForm()
    return render(request, 'services/form.html', {'form': form, 'title': 'Record Service'})
