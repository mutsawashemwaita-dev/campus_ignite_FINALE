import calendar as py_calendar
import datetime
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .views import _collect_events, EVENT_LABELS


def _year_events_by_month(year):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    events = _collect_events(start=start, end=end)

    by_month = defaultdict(list)
    for e in events:
        d = datetime.date.fromisoformat(e['start'])
        by_month[d.month].append({
            'date': d,
            'title': e['title'],
            'type': e['extendedProps']['type'],
            'time': e['extendedProps']['time'],
            'description': e['extendedProps']['description'],
        })

    months = []
    for m in range(1, 13):
        items = sorted(by_month.get(m, []), key=lambda x: x['date'])
        months.append({'name': py_calendar.month_name[m], 'items': items})
    return months


@login_required
def print_calendar_year(request):
    year = request.GET.get('year')
    try:
        year = int(year)
    except (TypeError, ValueError):
        year = datetime.date.today().year

    months = _year_events_by_month(year)
    total = sum(len(m['items']) for m in months)

    return render(request, 'print/calendar_year.html', {
        'year': year,
        'months': months,
        'total': total,
    })