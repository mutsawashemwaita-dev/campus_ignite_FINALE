import datetime
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

CI_NAVY  = colors.HexColor('#1A3C6E')
CI_GOLD  = colors.HexColor('#C8A951')
CI_LIGHT = colors.HexColor('#E8F0FB')
CI_WHITE = colors.white
CI_GREY  = colors.HexColor('#666666')


def _doc(buffer, title):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
        author='Campus Ignite'
    )


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('CITitle', fontSize=18, textColor=CI_WHITE, fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CISub',   fontSize=9,  textColor=CI_LIGHT, fontName='Helvetica'))
    s.add(ParagraphStyle('CIH2',    fontSize=12, textColor=CI_NAVY,  fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4))
    s.add(ParagraphStyle('CIH3',    fontSize=10, textColor=CI_NAVY,  fontName='Helvetica-Bold', spaceBefore=6,  spaceAfter=3))
    s.add(ParagraphStyle('CIBody',  fontSize=9,  textColor=colors.HexColor('#222'), fontName='Helvetica', spaceAfter=4, leading=13))
    s.add(ParagraphStyle('CILabel', fontSize=8,  textColor=CI_GREY,  fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CIGold',  fontSize=9,  textColor=CI_GOLD,  fontName='Helvetica-Bold', spaceAfter=2))
    s.add(ParagraphStyle('CIFoot',  fontSize=8,  textColor=CI_GREY,  fontName='Helvetica', alignment=1))
    return s


def _header(story, s, title, sub=''):
    d = [[Paragraph(title, s['CITitle']),
          Paragraph('Campus Ignite<br/><font size="8">Campus Christian Institution</font>', s['CISub'])]]
    t = Table(d, colWidths=[12 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CI_NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (0, -1), 16),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('RIGHTPADDING', (1, 0), (1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    if sub:
        story.append(Spacer(1, 4))
        story.append(Paragraph(sub, s['CIBody']))
    story.append(Spacer(1, 8))


def _meta(story, s, items):
    cells = [[Paragraph(f'<b>{k}:</b> {v}', s['CIBody']) for k, v in items]]
    t = Table(cells, colWidths=[17 * cm / len(items)] * len(items))
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CI_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 2, CI_GOLD),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def _sec(story, s, title):
    story.append(Spacer(1, 6))
    story.append(Paragraph(title, s['CIH2']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=CI_GOLD))
    story.append(Spacer(1, 6))


def _footer(story, s):
    story.append(Spacer(1, 16))
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
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CI_WHITE, CI_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]
    if header:
        style += [
            ('BACKGROUND', (0, 0), (-1, 0), CI_NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), CI_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style))
    return t
