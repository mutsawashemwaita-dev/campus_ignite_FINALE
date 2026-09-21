from io import BytesIO
from django.contrib.auth.decorators import login_required
from reportlab.lib.units import cm

from apps.departments.pdf_views import _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp
from .models import StudentAnchor


@login_required
def pdf_anchor_list(request):
    anchors = StudentAnchor.objects.filter(is_active=True).select_related('user').order_by('user__first_name')

    buf = BytesIO()
    doc = _doc(buf, 'Student Anchors')
    s = _styles()
    story = []

    _header(story, s, 'Student Anchors')
    _meta(story, s, [('Total Anchors', str(anchors.count()))])

    rows = [['#', 'Full Name', 'Since']] + [
        [str(i), a.user.get_full_name(), a.date_assigned.strftime('%d %b %Y')]
        for i, a in enumerate(anchors, 1)
    ]
    story.append(_tbl(rows, [2 * cm, 10 * cm, 5 * cm]))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, 'student_anchors.pdf')