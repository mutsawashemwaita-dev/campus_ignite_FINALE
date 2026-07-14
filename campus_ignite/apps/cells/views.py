import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import role_required
from apps.accounts.models import CustomUser
from apps.pastors.models import Pastor
from apps.notifications.utils import create_notification
from .models import Cell, CellMeetingReport, CellEvent, ConsolidatedCellReport
from .forms import (
    CellForm, CellMeetingReportForm, CellEventForm, ConsolidatedReportForm
)


@login_required
def cell_list(request):
    cells = Cell.objects.filter(is_active=True).select_related('cell_type', 'facilitator', 'second_in_cmd')
    return render(request, 'cells/list.html', {'cells': cells})


@login_required
def cell_detail(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    reports = cell.reports.select_related('facilitated_by').all()
    events = cell.events.filter(event_date__gte=__import__('datetime').date.today()).order_by('event_date')
    return render(request, 'cells/detail.html', {
        'cell': cell,
        'reports': reports,
        'events': events,
    })


@login_required
@role_required('admin', 'pastor', 'cell_leader')
def cell_create(request):
    if request.method == 'POST':
        form = CellForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cell created successfully.')
            return redirect('cell_list')
    else:
        form = CellForm()
    return render(request, 'cells/form.html', {'form': form, 'title': 'Create Cell'})


@login_required
@role_required('admin', 'pastor', 'cell_leader')
def cell_update(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    if request.method == 'POST':
        form = CellForm(request.POST, instance=cell)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cell updated.')
            return redirect('cell_detail', pk=pk)
    else:
        form = CellForm(instance=cell)
    return render(request, 'cells/form.html', {'form': form, 'title': 'Edit Cell'})


@login_required
def meeting_report_create(request, cell_pk):
    cell = get_object_or_404(Cell, pk=cell_pk)
    if request.method == 'POST':
        form = CellMeetingReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.cell = cell
            report.submitted_by = request.user
            report.save()
            messages.success(request, 'Meeting report submitted.')
            return redirect('cell_detail', pk=cell_pk)
    else:
        form = CellMeetingReportForm(initial={'facilitated_by': request.user})
    return render(request, 'cells/meeting_report_form.html', {'form': form, 'cell': cell})


@login_required
def cell_event_create(request, cell_pk):
    cell = get_object_or_404(Cell, pk=cell_pk)
    if request.method == 'POST':
        form = CellEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.cell = cell
            event.created_by = request.user
            event.save()
            # Notify all leaders about the new event
            _notify_leaders_of_event(event)
            messages.success(request, 'Event added to calendar. Leaders have been notified.')
            return redirect('cell_detail', pk=cell_pk)
    else:
        form = CellEventForm()
    return render(request, 'cells/calendar_event_form.html', {'form': form, 'cell': cell})


def _notify_leaders_of_event(event):
    """Notify all leadership and pastors about a new cell event."""
    from apps.leadership.models import LeadershipAssignment
    from datetime import date

    msg = f"New event: '{event.title}' on {event.event_date} for {event.cell.name}."

    # Notify cell leader & 2IC
    for uid in event.cell.get_leader_ids():
        create_notification(
            recipient_id=uid,
            title=f"New Cell Event – {event.cell.name}",
            message=msg,
            source_type='cell_event',
            source_id=event.pk,
        )

    # Notify active leadership holders
    for assignment in LeadershipAssignment.objects.filter(is_active=True, year=date.today().year):
        create_notification(
            recipient=assignment.leader,
            title=f"Cell Calendar – {event.cell.name}",
            message=msg,
            source_type='cell_event',
            source_id=event.pk,
        )

    # Notify pastors
    for pastor in Pastor.objects.filter(is_active=True).select_related('user'):
        create_notification(
            recipient=pastor.user,
            title=f"Cell Event Notification",
            message=msg,
            source_type='cell_event',
            source_id=event.pk,
        )


@login_required
def cell_events_json(request, cell_pk):
    """Return events as JSON for FullCalendar."""
    cell = get_object_or_404(Cell, pk=cell_pk)
    events = [
        {
            'id': e.pk,
            'title': e.title,
            'start': str(e.event_date),
            'description': e.description,
        }
        for e in cell.events.all()
    ]
    return JsonResponse(events, safe=False)


@login_required
@role_required('cell_leader', 'admin', 'pastor')
def consolidated_report_create(request):
    if request.method == 'POST':
        form = ConsolidatedReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.prepared_by = request.user
            report.sent_to_pastors = True
            report.save()
            form.save_m2m()
            # Notify pastors
            for pastor in Pastor.objects.filter(is_active=True).select_related('user'):
                create_notification(
                    recipient=pastor.user,
                    title='New Consolidated Cell Report',
                    message=f'A consolidated cell report for {report.period_start} to {report.period_end} has been submitted.',
                    source_type='consolidated_report',
                    source_id=report.pk,
                )
            messages.success(request, 'Consolidated report sent to pastors.')
            return redirect('dashboard')
    else:
        form = ConsolidatedReportForm(user=request.user)
    return render(request, 'cells/consolidated_report.html', {'form': form})
