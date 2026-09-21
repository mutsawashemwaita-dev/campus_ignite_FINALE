from io import BytesIO
from django.contrib.auth.decorators import login_required
from reportlab.lib.units import cm

from apps.departments.pdf_views import _doc, _styles, _header, _meta, _sec, _footer, _tbl, _resp
from .models import CustomUser


@login_required
def pdf_alumni_list(request):
    alumni = CustomUser.objects.filter(is_alumni=True, is_active=True).order_by('first_name', 'last_name')

    buf = BytesIO()
    doc = _doc(buf, 'Campus Ignite Alumni')
    s = _styles()
    story = []

    _header(story, s, 'Campus Ignite Alumni')
    _meta(story, s, [('Total Alumni', str(alumni.count()))])

    rows = [['#', 'Full Name']] + [
        [str(i), person.get_full_name()] for i, person in enumerate(alumni, 1)
    ]
    story.append(_tbl(rows, [2 * cm, 15 * cm]))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, 'campus_ignite_alumni.pdf')