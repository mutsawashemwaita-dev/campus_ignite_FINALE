import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from apps.cells.models import CellEvent
from apps.departments.models import DepartmentEvent
from apps.services.models import ServiceRecord

# Colour keys used consistently across the calendar view, JSON feed, legend and print/PDF output.
EVENT_COLORS = {
    'cell':       '#1A3C6E',   # navy
    'department': '#C8A951',   # gold
    'service':    '#198754',   # green
}

EVENT_LABELS = {
    'cell':       'Cell Event',
    'department': 'Department Event',
    'service':    'Service',
}


def _parse_date(value):
    """Best-effort parse of a date coming from FullCalendar's fetch params (ISO or with a time component)."""
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value[:10])
    except (ValueError, TypeError):
        return None


def _collect_events(start=None, end=None, types=None):
    """Build a unified list of calendar events from Cells, Departments and Services.

    start/end: optional datetime.date bounds (inclusive) to filter by.
    types: optional iterable restricting to a subset of {'cell','department','service'}.
    """
    types = set(types) if types else {'cell', 'department', 'service'}
    events = []

    if 'cell' in types:
        qs = CellEvent.objects.select_related('cell').all()
        if start:
            qs = qs.filter(event_date__gte=start)
        if end:
            qs = qs.filter(event_date__lte=end)
        for e in qs:
            events.append({
                'id': f'cell-{e.pk}',
                'title': f'{e.title} ({e.cell.name})',
                'start': str(e.event_date),
                'allDay': True,
                'color': EVENT_COLORS['cell'],
                'extendedProps': {
                    'type': EVENT_LABELS['cell'],
                    'description': e.description,
                    'time': e.event_time.strftime('%H:%M') if e.event_time else '',
                    'group': e.cell.name,
                    'url': f'/cells/{e.cell_id}/',
                },
            })

    if 'department' in types:
        qs = DepartmentEvent.objects.select_related('department').all()
        if start:
            qs = qs.filter(event_date__gte=start)
        if end:
            qs = qs.filter(event_date__lte=end)
        for e in qs:
            events.append({
                'id': f'dept-{e.pk}',
                'title': f'{e.title} ({e.department.name})',
                'start': str(e.event_date),
                'allDay': True,
                'color': EVENT_COLORS['department'],
                'extendedProps': {
                    'type': EVENT_LABELS['department'],
                    'description': e.description,
                    'time': e.event_time.strftime('%H:%M') if e.event_time else '',
                    'group': e.department.name,
                    'url': f'/departments/{e.department_id}/',
                },
            })

    if 'service' in types:
        qs = ServiceRecord.objects.select_related('preacher').all()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        for s in qs:
            preacher = s.guest_preacher or (s.preacher.get_full_name() if s.preacher else '')
            events.append({
                'id': f'svc-{s.pk}',
                'title': s.message_title or 'Service',
                'start': str(s.date),
                'allDay': True,
                'color': EVENT_COLORS['service'],
                'extendedProps': {
                    'type': EVENT_LABELS['service'],
                    'description': preacher and f'Preacher: {preacher}' or '',
                    'time': '',
                    'group': 'Sunday Service',
                    'url': '/services/',
                },
            })

    return events


@login_required
def calendar_view(request):
    year = request.GET.get('year')
    try:
        year = int(year)
    except (TypeError, ValueError):
        year = datetime.date.today().year

    return render(request, 'schedule/calendar.html', {
        'year': year,
        'legend': [
            {'label': EVENT_LABELS['cell'], 'color': EVENT_COLORS['cell']},
            {'label': EVENT_LABELS['department'], 'color': EVENT_COLORS['department']},
            {'label': EVENT_LABELS['service'], 'color': EVENT_COLORS['service']},
        ],
    })


@login_required
def calendar_events_json(request):
    """JSON feed consumed by FullCalendar. Honors FullCalendar's start/end range params
    and an optional ?types=cell,department,service filter."""
    start = _parse_date(request.GET.get('start'))
    end = _parse_date(request.GET.get('end'))
    types_param = request.GET.get('types')
    types = [t.strip() for t in types_param.split(',') if t.strip()] if types_param else None

    events = _collect_events(start=start, end=end, types=types)
    return JsonResponse(events, safe=False)