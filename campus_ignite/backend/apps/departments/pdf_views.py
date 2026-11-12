from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer

# Shared ReportLab helpers from core
from apps.core.pdf import (
    _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp,
    CI_NAVY, CI_GOLD, CI_LIGHT, CI_WHITE, CI_GREY
)
from .models import Department

# Re-exports for backwards compatibility
from apps.cells.pdf_views import pdf_cell_reports, pdf_consolidated_report
from apps.services.pdf_views import pdf_service, pdf_services_all
from apps.notifications.pdf_views import pdf_notifications


@login_required
def pdf_department(request, pk):
    dept    = get_object_or_404(Department, pk=pk)
    members = dept.members.select_related('user').all()
    posts   = dept.posts.select_related('posted_by').all()
    buf = BytesIO()
    doc = _doc(buf, dept.name)
    s = _styles()
    story = []

    _header(story, s, dept.name, dept.description or '')
    _meta(story, s, [
        ('Type', dept.get_dept_type_display()),
        ('Members', str(members.count())),
        ('Leader', dept.leader.get_full_name() if dept.leader else '—'),
        ('2IC', dept.second_in_cmd.get_full_name() if dept.second_in_cmd else '—')
    ])
    _sec(story, s, 'Members')
    rows = [['#', 'Full Name', 'Username', 'Role', 'Date Joined']] + [
        [str(i), m.user.get_full_name(), m.user.username, m.role_in_dept or 'Member', str(m.date_joined)]
        for i, m in enumerate(members, 1)
    ]
    story.append(_tbl(rows, [1 * cm, 4 * cm, 3 * cm, 5 * cm, 3 * cm]))
    if posts:
        _sec(story, s, 'Posts & Announcements')
        for p in posts:
            story.append(Paragraph(f'{"[PINNED] " if p.is_pinned else ""}<b>{p.title}</b>', s['CIH3']))
            story.append(Paragraph(p.content, s['CIBody']))
            posted_by = p.posted_by.get_full_name() if p.posted_by else '—'
            story.append(Paragraph(f'By {posted_by} – {p.created_at.strftime("%d %b %Y")}', s['CILabel']))
            story.append(Spacer(1, 6))
    _footer(story, s)
    doc.build(story)
    return _resp(buf, f'{dept.name.replace(" ", "_")}.pdf')
