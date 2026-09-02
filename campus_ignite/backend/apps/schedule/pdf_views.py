import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from reportlab.lib.units import cm

from apps.departments.pdf_views import _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp
from .print_views import _year_events_by_month


@login_required
def pdf_calendar_year(request):
    year = request.GET.get('year')
    try:
        year = int(year)
    except (TypeError, ValueError):
        year = datetime.date.today().year

    months = _year_events_by_month(year)
    total = sum(len(m['items']) for m in months)

    buf = BytesIO()
    doc = _doc(buf, f'Calendar {year}')
    s = _styles()
    story = []

    _header(story, s, f'{year} Calendar – All Events')
    _meta(story, s, [('Year', str(year)), ('Total Events', str(total))])

    for month in months:
        if not month['items']:
            continue
        _sec(story, s, month['name'])
        rows = [['Date', 'Event', 'Type', 'Time']] + [
            [item['date'].strftime('%d %b'), item['title'], item['type'], item['time'] or '—']
            for item in month['items']
        ]
        story.append(_tbl(rows, [2.5 * cm, 8 * cm, 4 * cm, 2.5 * cm]))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, f'calendar_{year}.pdf')