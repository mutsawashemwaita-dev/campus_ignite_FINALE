import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from apps.notifications.utils import create_notification
from .models import Cell, CellMeetingReport, CellEvent, ConsolidatedCellReport, CellType, CellMember
from .forms import CellForm, CellMeetingReportForm, CellEventForm, ConsolidatedReportForm


@login_required
def cell_list(request):
    cells = Cell.objects.filter(is_active=True).select_related('cell_type', 'facilitator', 'second_in_cmd')
    return render(request, 'cells/list.html', {'cells': cells})


@login_required
def cell_detail(request, pk):
    cell         = get_object_or_404(Cell, pk=pk)
    reports      = cell.reports.select_related('facilitated_by').all()
    events       = cell.events.filter(event_date__gte=datetime.date.today()).order_by('event_date')
    cell_members = cell.cell_members.select_related('user').all()
    return render(request, 'cells/detail.html', {
        'cell': cell, 'reports': reports, 'events': events, 'cell_members': cell_members,
    })


@login_required
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
def cell_update(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    if request.method == 'POST':
        form = CellForm(request.POST)
        if form.is_valid():
            form.save(instance=cell)
            messages.success(request, 'Cell updated.')
            return redirect('cell_detail', pk=pk)
    else:
        form = CellForm(initial={
            'name':                   cell.name,
            'facilitator_username':   cell.facilitator.username,
            'second_in_cmd_username': cell.second_in_cmd.username if cell.second_in_cmd else '',
            'cell_type_name':         cell.cell_type.name if cell.cell_type else '',
            'meeting_day':            cell.meeting_day,
            'venue':                  cell.venue,
            'meeting_time':           cell.meeting_time,
        })
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
        form = CellMeetingReportForm(initial={'facilitated_by_username': request.user.username})
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
            _notify_leaders_of_event(event)
            messages.success(request, 'Event added. Leaders have been notified.')
            return redirect('cell_detail', pk=cell_pk)
    else:
        form = CellEventForm()
    return render(request, 'cells/calendar_event_form.html', {'form': form, 'cell': cell})


def _notify_leaders_of_event(event):
    from apps.leadership.models import LeadershipAssignment
    from apps.pastors.models import Pastor
    msg = f"New event: '{event.title}' on {event.event_date} for {event.cell.name}."
    for uid in event.cell.get_leader_ids():
        create_notification(recipient_id=uid, title=f"New Cell Event – {event.cell.name}",
                            message=msg, source_type='cell_event', source_id=event.pk)
    for a in LeadershipAssignment.objects.filter(is_active=True, year=datetime.date.today().year):
        create_notification(recipient=a.leader, title=f"Cell Calendar – {event.cell.name}",
                            message=msg, source_type='cell_event', source_id=event.pk)
    for p in Pastor.objects.filter(is_active=True).select_related('user'):
        create_notification(recipient=p.user, title="Cell Event Notification",
                            message=msg, source_type='cell_event', source_id=event.pk)


@login_required
def cell_events_json(request, cell_pk):
    cell   = get_object_or_404(Cell, pk=cell_pk)
    events = [{'id': e.pk, 'title': e.title, 'start': str(e.event_date), 'description': e.description}
              for e in cell.events.all()]
    return JsonResponse(events, safe=False)


@login_required
def consolidated_report_create(request):
    if request.method == 'POST':
        form = ConsolidatedReportForm(request.POST)
        if form.is_valid():
            from apps.pastors.models import Pastor
            report = ConsolidatedCellReport.objects.create(
                prepared_by  = request.user,
                period_start = form.cleaned_data['period_start'],
                period_end   = form.cleaned_data['period_end'],
                summary      = (
                    f"CELLS: {form.cleaned_data['cell_names']}\n\n"
                    f"SUMMARY:\n{form.cleaned_data['summary']}\n\n"
                    f"TOTAL HEADCOUNT: {form.cleaned_data['total_headcount']}\n\n"
                    f"HIGHLIGHTS:\n{form.cleaned_data.get('highlights','')}\n\n"
                    f"CHALLENGES:\n{form.cleaned_data.get('challenges','')}"
                ),
                sent_to_pastors=True,
            )
            for p in Pastor.objects.filter(is_active=True).select_related('user'):
                create_notification(
                    recipient=p.user,
                    title='New Consolidated Cell Report',
                    message=f'Report for {report.period_start} to {report.period_end} submitted by {request.user.get_full_name()}.',
                    source_type='consolidated_report', source_id=report.pk,
                )
            messages.success(request, 'Consolidated report sent to pastors successfully.')
            return redirect('dashboard')
    else:
        form = ConsolidatedReportForm()
    return render(request, 'cells/consolidated_report.html', {'form': form})


# ── Cell Members ─────────────────────────────────────────────
@login_required
def cell_members(request, pk):
    cell    = get_object_or_404(Cell, pk=pk)
    members = cell.cell_members.select_related('user').all()
    return render(request, 'cells/members.html', {'cell': cell, 'members': members})


@login_required
def add_cell_member(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    if request.method == 'POST':
        username_or_name = request.POST.get('member_search', '').strip()
        attendance       = request.POST.get('attendance', 'regular')
        notes            = request.POST.get('notes', '').strip()

        from apps.accounts.models import CustomUser
        user = None
        try:
            user = CustomUser.objects.get(username=username_or_name)
        except CustomUser.DoesNotExist:
            parts = username_or_name.split()
            if len(parts) >= 2:
                qs = CustomUser.objects.filter(
                    first_name__iexact=parts[0],
                    last_name__iexact=' '.join(parts[1:])
                )
                if qs.exists():
                    user = qs.first()

        if not user:
            messages.error(request, f'No person found with username or name "{username_or_name}". Add them in Manage People first.')
            return redirect('cell_members', pk=pk)

        member, created = CellMember.objects.get_or_create(
            cell=cell, user=user,
            defaults={'attendance': attendance, 'notes': notes}
        )
        if created:
            messages.success(request, f'{user.get_full_name()} added to {cell.name} as {attendance}.')
        else:
            member.attendance = attendance
            member.notes = notes
            member.save()
            messages.info(request, f'{user.get_full_name()} updated in {cell.name}.')
    return redirect('cell_members', pk=pk)


@login_required
def remove_cell_member(request, pk, member_pk):
    cell   = get_object_or_404(Cell, pk=pk)
    member = get_object_or_404(CellMember, pk=member_pk, cell=cell)
    name   = member.user.get_full_name()
    member.delete()
    messages.success(request, f'{name} removed from {cell.name}.')
    return redirect('cell_members', pk=pk)


@login_required
def update_member_attendance(request, pk, member_pk):
    cell   = get_object_or_404(Cell, pk=pk)
    member = get_object_or_404(CellMember, pk=member_pk, cell=cell)
    attendance = request.POST.get('attendance', member.attendance)
    member.attendance = attendance
    member.save()
    messages.success(request, f'{member.user.get_full_name()} updated to {attendance}.')
    return redirect('cell_members', pk=pk)


@login_required
def consolidated_report_list(request):
    """Pastors and admins see all consolidated reports."""
    from apps.cells.models import ConsolidatedCellReport
    reports = ConsolidatedCellReport.objects.select_related('prepared_by').order_by('-submitted_at')
    return render(request, 'cells/consolidated_report_list.html', {'reports': reports})


@login_required
def consolidated_report_detail(request, pk):
    report = get_object_or_404(ConsolidatedCellReport, pk=pk)
    return render(request, 'cells/consolidated_report_detail.html', {'report': report})
