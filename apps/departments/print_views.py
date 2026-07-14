from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from apps.cells.models import Cell, CellMeetingReport
from apps.services.models import ServiceRecord
from apps.notifications.models import Notification
from apps.departments.models import Department


@login_required
def print_cell_reports(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    reports = cell.reports.select_related('facilitated_by', 'submitted_by').all()
    return render(request, 'print/cell_reports.html', {'cell': cell, 'reports': reports})


@login_required
def print_service(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    return render(request, 'print/service.html', {'service': service})


@login_required
def print_services_all(request):
    services = ServiceRecord.objects.select_related('preacher', 'recorded_by').all()
    return render(request, 'print/services_all.html', {'services': services})


@login_required
def print_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'print/notifications.html', {'notifications': notifications})


@login_required
def print_department(request, pk):
    dept    = get_object_or_404(Department, pk=pk)
    members = dept.members.select_related('user').all()
    posts   = dept.posts.select_related('posted_by').all()
    return render(request, 'print/department.html', {'dept': dept, 'members': members, 'posts': posts})


@login_required
def print_consolidated_report(request, pk):
    from apps.cells.models import ConsolidatedCellReport
    report = get_object_or_404(ConsolidatedCellReport, pk=pk)
    return render(request, 'print/consolidated_report.html', {'report': report})
