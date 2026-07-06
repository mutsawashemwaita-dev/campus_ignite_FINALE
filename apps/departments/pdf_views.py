from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from io import BytesIO
import datetime

CI_NAVY  = colors.HexColor('#1A3C6E')
CI_GOLD  = colors.HexColor('#C8A951')
CI_LIGHT = colors.HexColor('#E8F0FB')
CI_WHITE = colors.white
CI_GREY  = colors.HexColor('#666666')


def _doc(buffer, title):
    return SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title=title, author='Campus Ignite')


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('CITitle', fontSize=18, textColor=CI_WHITE,  fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CISub',   fontSize=9,  textColor=CI_LIGHT,  fontName='Helvetica'))
    s.add(ParagraphStyle('CIH2',    fontSize=12, textColor=CI_NAVY,   fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4))
    s.add(ParagraphStyle('CIH3',    fontSize=10, textColor=CI_NAVY,   fontName='Helvetica-Bold', spaceBefore=6,  spaceAfter=3))
    s.add(ParagraphStyle('CIBody',  fontSize=9,  textColor=colors.HexColor('#222'), fontName='Helvetica', spaceAfter=4, leading=13))
    s.add(ParagraphStyle('CILabel', fontSize=8,  textColor=CI_GREY,   fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CIGold',  fontSize=9,  textColor=CI_GOLD,   fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CIFoot',  fontSize=8,  textColor=CI_GREY,   fontName='Helvetica', alignment=1))
    return s


def _header(story, s, title, sub=''):
    d = [[Paragraph(title, s['CITitle']),
          Paragraph(f'Campus Ignite<br/><font size="8">Campus Christian Institution</font>', s['CISub'])]]
    t = Table(d, colWidths=[12*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),CI_NAVY),
        ('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),14),
        ('LEFTPADDING',(0,0),(0,-1),16),('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('RIGHTPADDING',(1,0),(1,-1),14),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(t)
    if sub: story.append(Spacer(1,4)); story.append(Paragraph(sub, s['CIBody']))
    story.append(Spacer(1,8))


def _meta(story, s, items):
    cells = [[Paragraph(f'<b>{k}:</b> {v}', s['CIBody']) for k,v in items]]
    t = Table(cells, colWidths=[17*cm/len(items)]*len(items))
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),CI_LIGHT),
        ('LEFTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),2,CI_GOLD),
    ]))
    story.append(t); story.append(Spacer(1,10))


def _sec(story, s, title):
    story.append(Spacer(1,6))
    story.append(Paragraph(title, s['CIH2']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=CI_GOLD))
    story.append(Spacer(1,6))


def _footer(story, s):
    story.append(Spacer(1,16))
    story.append(HRFlowable(width='100%', thickness=1, color=CI_LIGHT))
    story.append(Paragraph(f'Campus Ignite | Generated {datetime.date.today().strftime("%d %B %Y")}', s['CIFoot']))


def _resp(buf, fname):
    buf.seek(0)
    r = HttpResponse(buf, content_type='application/pdf')
    r['Content-Disposition'] = f'attachment; filename="{fname}"'
    return r


def _tbl(rows, widths, header=True):
    t = Table(rows, colWidths=widths)
    style = [
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[CI_WHITE,CI_LIGHT]),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#dee2e6')),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),6),
    ]
    if header:
        style += [
            ('BACKGROUND',(0,0),(-1,0),CI_NAVY),
            ('TEXTCOLOR',(0,0),(-1,0),CI_WHITE),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style))
    return t


# ── Cell Reports ─────────────────────────────────────────────
@login_required
def pdf_cell_reports(request, pk):
    from apps.cells.models import Cell
    cell = get_object_or_404(Cell, pk=pk)
    reports = cell.reports.select_related('facilitated_by','submitted_by').all()
    buf = BytesIO(); doc = _doc(buf, f'{cell.name} Reports'); s = _styles(); story = []
    _header(story, s, f'{cell.name} – Meeting Reports')
    _meta(story, s, [('Cell',cell.name),('Facilitator',cell.facilitator.get_full_name()),
                     ('2IC',cell.second_in_cmd.get_full_name() if cell.second_in_cmd else '—'),
                     ('Total Reports',str(reports.count()))])
    for r in reports:
        _sec(story, s, f'Report – {r.date}  |  By {r.facilitated_by.get_full_name()}')
        mt = [['Started','Ended','Headcount','Submitted'],[str(r.time_started)[:5],str(r.time_ended)[:5],str(r.head_count),r.submitted_at.strftime('%d %b %Y')]]
        story.append(_tbl(mt,[3*cm,3*cm,3*cm,8*cm]))
        story.append(Spacer(1,6))
        story.append(Paragraph('<b>Summary</b>', s['CILabel']))
        story.append(Paragraph(r.summary or '—', s['CIBody']))
        if r.went_right: story.append(Paragraph('What Went Right', s['CIGold'])); story.append(Paragraph(r.went_right, s['CIBody']))
        if r.went_wrong: story.append(Paragraph('What Went Wrong', s['CILabel'])); story.append(Paragraph(r.went_wrong, s['CIBody']))
        if r.highlights: story.append(Paragraph('Highlights', s['CIGold'])); story.append(Paragraph(r.highlights, s['CIBody']))
    _footer(story, s); doc.build(story)
    return _resp(buf, f'{cell.name.replace(" ","_")}_reports.pdf')


# ── Single Service ───────────────────────────────────────────
@login_required
def pdf_service(request, pk):
    from apps.services.models import ServiceRecord
    svc = get_object_or_404(ServiceRecord, pk=pk)
    buf = BytesIO(); doc = _doc(buf, f'Service {svc.date}'); s = _styles(); story = []
    preacher = svc.guest_preacher or (svc.preacher.get_full_name() if svc.preacher else '—')
    _header(story, s, f'Service Record – {svc.date}')
    _meta(story, s, [('Date',str(svc.date)),('Preacher',preacher),('Headcount',str(svc.head_count)),('Recorded by',svc.recorded_by.get_full_name())])
    _sec(story, s, svc.message_title)
    story.append(Paragraph('<b>Message Summary</b>', s['CILabel']))
    story.append(Paragraph(svc.message_summary or '—', s['CIBody']))
    _sec(story, s, 'Flow of Service')
    for i, step in enumerate(svc.get_flow_list(), 1):
        story.append(Paragraph(f'{i}.  {step}', s['CIBody']))
    _footer(story, s); doc.build(story)
    return _resp(buf, f'service_{svc.date}.pdf')


# ── All Services ─────────────────────────────────────────────
@login_required
def pdf_services_all(request):
    from apps.services.models import ServiceRecord
    services = ServiceRecord.objects.select_related('preacher','recorded_by').all()
    buf = BytesIO(); doc = _doc(buf, 'All Services'); s = _styles(); story = []
    _header(story, s, 'All Service Records')
    _meta(story, s, [('Total Services', str(services.count()))])
    rows = [['Date','Preacher','Message Title','HC']] + [
        [str(sv.date), sv.guest_preacher or (sv.preacher.get_full_name() if sv.preacher else '—'),
         sv.message_title, str(sv.head_count)] for sv in services]
    story.append(_tbl(rows, [2.5*cm,4*cm,8*cm,2.5*cm]))
    _footer(story, s); doc.build(story)
    return _resp(buf, 'all_services.pdf')


# ── Notifications ────────────────────────────────────────────
@login_required
def pdf_notifications(request):
    from apps.notifications.models import Notification
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    buf = BytesIO(); doc = _doc(buf, 'Notifications'); s = _styles(); story = []
    _header(story, s, 'Notifications', f'For: {request.user.get_full_name()}')
    _meta(story, s, [('User',request.user.get_full_name()),('Total',str(notifs.count())),
                     ('Unread',str(notifs.filter(is_read=False).count()))])
    for n in notifs:
        status = 'UNREAD' if not n.is_read else 'Read'
        story.append(Paragraph(f'<b>{n.title}</b>  [{status}]', s['CIH3']))
        story.append(Paragraph(n.message, s['CIBody']))
        story.append(Paragraph(f'{n.created_at.strftime("%d %b %Y, %H:%M")}', s['CILabel']))
        story.append(HRFlowable(width='100%', thickness=0.5, color=CI_LIGHT))
        story.append(Spacer(1,4))
    _footer(story, s); doc.build(story)
    return _resp(buf, 'notifications.pdf')


# ── Department ───────────────────────────────────────────────
@login_required
def pdf_department(request, pk):
    from apps.departments.models import Department
    dept    = get_object_or_404(Department, pk=pk)
    members = dept.members.select_related('user').all()
    posts   = dept.posts.select_related('posted_by').all()
    buf = BytesIO(); doc = _doc(buf, dept.name); s = _styles(); story = []
    _header(story, s, dept.name, dept.description or '')
    _meta(story, s, [('Type',dept.get_dept_type_display()),('Members',str(members.count())),
                     ('Leader',dept.leader.get_full_name() if dept.leader else '—'),
                     ('2IC',dept.second_in_cmd.get_full_name() if dept.second_in_cmd else '—')])
    _sec(story, s, 'Members')
    rows = [['#','Full Name','Username','Role','Date Joined']] + [
        [str(i), m.user.get_full_name(), m.user.username, m.role_in_dept or 'Member', str(m.date_joined)]
        for i, m in enumerate(members, 1)]
    story.append(_tbl(rows, [1*cm,4*cm,3*cm,5*cm,3*cm]))
    if posts:
        _sec(story, s, 'Posts & Announcements')
        for p in posts:
            story.append(Paragraph(f'{"[PINNED] " if p.is_pinned else ""}<b>{p.title}</b>', s['CIH3']))
            story.append(Paragraph(p.content, s['CIBody']))
            story.append(Paragraph(f'By {p.posted_by.get_full_name()} – {p.created_at.strftime("%d %b %Y")}', s['CILabel']))
            story.append(Spacer(1,6))
    _footer(story, s); doc.build(story)
    return _resp(buf, f'{dept.name.replace(" ","_")}.pdf')
