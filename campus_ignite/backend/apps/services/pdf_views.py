from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph

from apps.core.pdf import _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp
from .models import ServiceRecord


@login_required
def pdf_service(request, pk):
    svc = get_object_or_404(ServiceRecord, pk=pk)
    buf = BytesIO()
    doc = _doc(buf, f'Service {svc.date}')
    s = _styles()
    story = []
    preacher = svc.guest_preacher or (svc.preacher.get_full_name() if svc.preacher else '—')
    recorded_by = svc.recorded_by.get_full_name() if svc.recorded_by else '—'

    _header(story, s, f'Service Record – {svc.date}')
    _meta(story, s, [
        ('Date', str(svc.date)),
        ('Preacher', preacher),
        ('Headcount', str(svc.head_count)),
        ('Recorded by', recorded_by)
    ])
    _sec(story, s, svc.message_title)
    story.append(Paragraph('<b>Message Summary</b>', s['CILabel']))
    story.append(Paragraph(svc.message_summary or '—', s['CIBody']))
    _sec(story, s, 'Flow of Service')
    for i, step in enumerate(svc.get_flow_list(), 1):
        story.append(Paragraph(f'{i}.  {step}', s['CIBody']))
    _footer(story, s)
    doc.build(story)
    return _resp(buf, f'service_{svc.date}.pdf')


@login_required
def pdf_services_all(request):
    services = ServiceRecord.objects.select_related('preacher', 'recorded_by').all()
    buf = BytesIO()
    doc = _doc(buf, 'All Services')
    s = _styles()
    story = []

    _header(story, s, 'All Service Records')
    _meta(story, s, [('Total Services', str(services.count()))])
    rows = [['Date', 'Preacher', 'Message Title', 'HC']] + [
        [
            str(sv.date),
            sv.guest_preacher or (sv.preacher.get_full_name() if sv.preacher else '—'),
            sv.message_title,
            str(sv.head_count)
        ]
        for sv in services
    ]
    story.append(_tbl(rows, [2.5 * cm, 4 * cm, 8 * cm, 2.5 * cm]))
    _footer(story, s)
    doc.build(story)
    return _resp(buf, 'all_services.pdf')
