from django.urls import path
from . import views
from . import print_views
from . import pdf_views

urlpatterns = [
    path('', views.calendar_view, name='org_calendar'),
    path('events/', views.calendar_events_json, name='org_calendar_events'),
    path('print/', print_views.print_calendar_year, name='print_calendar_year'),
    path('pdf/', pdf_views.pdf_calendar_year, name='pdf_calendar_year'),
]