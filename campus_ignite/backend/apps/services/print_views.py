from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import ServiceRecord


@login_required
def print_service(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    return render(request, 'print/service.html', {'service': service})


@login_required
def print_services_all(request):
    services = ServiceRecord.objects.select_related('preacher', 'recorded_by').all()
    return render(request, 'print/services_all.html', {'services': services})
