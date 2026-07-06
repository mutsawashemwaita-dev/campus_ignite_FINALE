from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from apps.accounts.decorators import role_required
from .models import ServiceRecord
from .forms import ServiceRecordForm


@login_required
def service_list(request):
    services = ServiceRecord.objects.select_related(
        'preacher',
        'recorded_by'
    ).all()
    return render(request, 'services/list.html', {'services': services})


@login_required
def service_detail(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    return render(request, 'services/detail.html', {'service': service})


@login_required
@role_required('admin', 'pastor', 'leadership')
def service_create(request):
    if request.method == 'POST':
        form = ServiceRecordForm(request.POST)

        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()

            messages.success(request, 'Service record saved.')
            return redirect('service_list')
    else:
        form = ServiceRecordForm()

    return render(request, 'services/form.html', {
        'form': form,
        'title': 'Record Service'
    })


# ===========================
# DOWNLOAD SERVICE RECORDS PDF
# ===========================

@login_required
def service_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="service_records.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Campus Ignite Church</b>", styles['Title']))
    elements.append(Paragraph("Service Records Report", styles['Heading2']))
    elements.append(Spacer(1, 12))

    data = [[
        "Date",
        "Preacher",
        "Message Title",
        "Head Count"
    ]]

    services = ServiceRecord.objects.select_related('preacher').order_by('-date')

    for service in services:

        if service.guest_preacher:
            preacher = service.guest_preacher
        elif service.preacher:
            preacher = service.preacher.get_full_name()
        else:
            preacher = "-"

        data.append([
            str(service.date),
            preacher,
            service.message_title,
            str(service.head_count)
        ])

    table = Table(
        data,
        colWidths=[
            1.2 * inch,
            2.0 * inch,
            2.8 * inch,
            1.0 * inch
        ]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)

    doc.build(elements)

    return response