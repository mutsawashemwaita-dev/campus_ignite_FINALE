from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer

from apps.core.pdf import _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp
from .models import Cell, ConsolidatedCellReport


@login_required
def pdf_cell_reports(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    reports = cell.reports.select_related('facilitated_by', 'submitted_by').all()
    buf = BytesIO()
    doc = _doc(buf, f'{cell.name} Reports')
    s = _styles()
    story = []

    _header(story, s, f'{cell.name} – Meeting Reports')
    _meta(story, s, [
        ('Cell', cell.name),
        ('Facilitator', cell.facilitator.get_full_name() if cell.facilitator else '—'),
        ('2IC', cell.second_in_cmd.get_full_name() if cell.second_in_cmd else '—'),
        ('Total Reports', str(reports.count()))
    ])

    for r in reports:
        facil_name = r.facilitated_by.get_full_name() if r.facilitated_by else '—'
        _sec(story, s, f'Report – {r.date}  |  By {facil_name}')
        mt = [
            ['Started', 'Ended', 'Headcount', 'Submitted'],
            [str(r.time_started)[:5], str(r.time_ended)[:5], str(r.head_count), r.submitted_at.strftime('%d %b %Y')]
        ]
        story.append(_tbl(mt, [3 * cm, 3 * cm, 3 * cm, 8 * cm]))
        story.append(Spacer(1, 6))
        story.append(Paragraph('<b>Summary</b>', s['CILabel']))
        story.append(Paragraph(r.summary or '—', s['CIBody']))
        if r.went_right:
            story.append(Paragraph('What Went Right', s['CIGold']))
            story.append(Paragraph(r.went_right, s['CIBody']))
        if r.went_wrong:
            story.append(Paragraph('What Went Wrong', s['CILabel']))
            story.append(Paragraph(r.went_wrong, s['CIBody']))
        if r.highlights:
            story.append(Paragraph('Highlights', s['CIGold']))
            story.append(Paragraph(r.highlights, s['CIBody']))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, f'{cell.name.replace(" ", "_")}_reports.pdf')


@login_required
def pdf_consolidated_report(request, pk):
    report = get_object_or_404(ConsolidatedCellReport, pk=pk)

    buf = BytesIO()
    doc = _doc(buf, f'Consolidated Report {report.period_start}')
    s = _styles()
    story = []

    _header(story, s, 'Consolidated Cell Report')
    _meta(story, s, [
        ('Period', f'{report.period_start} to {report.period_end}'),
        ('Prepared By', report.prepared_by.get_full_name() if report.prepared_by else '—'),
        ('Submitted', report.submitted_at.strftime('%d %b %Y, %H:%M')),
        ('Status', 'Sent to Pastors' if report.sent_to_pastors else 'Draft'),
    ])

    _sec(story, s, 'Report Content')
    for line in report.summary.split('\n'):
        if line.strip():
            story.append(Paragraph(line.strip(), s['CIBody']))
        else:
            story.append(Spacer(1, 4))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, f'consolidated_report_{report.period_start}.pdf')
