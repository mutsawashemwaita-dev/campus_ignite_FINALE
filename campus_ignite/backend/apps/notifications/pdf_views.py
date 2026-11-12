from io import BytesIO
from django.contrib.auth.decorators import login_required
from reportlab.platypus import Paragraph, Spacer, HRFlowable

from apps.core.pdf import _doc, _styles, _header, _meta, _footer, _resp, CI_LIGHT
from .models import Notification


@login_required
def pdf_notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    buf = BytesIO()
    doc = _doc(buf, 'Notifications')
    s = _styles()
    story = []

    _header(story, s, 'Notifications', f'For: {request.user.get_full_name()}')
    _meta(story, s, [
        ('User', request.user.get_full_name()),
        ('Total', str(notifs.count())),
        ('Unread', str(notifs.filter(is_read=False).count()))
    ])

    for n in notifs:
        status = 'UNREAD' if not n.is_read else 'Read'
        story.append(Paragraph(f'<b>{n.title}</b>  [{status}]', s['CIH3']))
        story.append(Paragraph(n.message, s['CIBody']))
        story.append(Paragraph(f'{n.created_at.strftime("%d %b %Y, %H:%M")}', s['CILabel']))
        story.append(HRFlowable(width='100%', thickness=0.5, color=CI_LIGHT))
        story.append(Spacer(1, 4))

    _footer(story, s)
    doc.build(story)
    return _resp(buf, 'notifications.pdf')
