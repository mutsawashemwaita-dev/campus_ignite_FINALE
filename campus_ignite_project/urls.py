from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.departments.print_views import (
    print_cell_reports, print_service, print_services_all,
    print_notifications, print_department
)
from apps.departments.pdf_views import (
    pdf_cell_reports, pdf_service, pdf_services_all,
    pdf_notifications, pdf_department
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.accounts.dashboard_urls')),
    path('pastors/', include('apps.pastors.urls')),
    path('leadership/', include('apps.leadership.urls')),
    path('cells/', include('apps.cells.urls')),
    path('services/', include('apps.services.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('departments/', include('apps.departments.urls')),
    # Print (browser)
    path('print/cells/<int:pk>/reports/',  print_cell_reports,  name='print_cell_reports'),
    path('print/services/<int:pk>/',       print_service,       name='print_service'),
    path('print/services/',                print_services_all,  name='print_services_all'),
    path('print/notifications/',           print_notifications, name='print_notifications'),
    path('print/departments/<int:pk>/',    print_department,    name='print_department'),
    # PDF download
    path('pdf/cells/<int:pk>/reports/',    pdf_cell_reports,    name='pdf_cell_reports'),
    path('pdf/services/<int:pk>/',         pdf_service,         name='pdf_service'),
    path('pdf/services/',                  pdf_services_all,    name='pdf_services_all'),
    path('pdf/notifications/',             pdf_notifications,   name='pdf_notifications'),
    path('pdf/departments/<int:pk>/',      pdf_department,      name='pdf_department'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
