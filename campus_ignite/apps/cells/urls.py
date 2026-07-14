from django.urls import path
from . import views

urlpatterns = [
    path('', views.cell_list, name='cell_list'),
    path('add/', views.cell_create, name='cell_create'),
    path('<int:pk>/', views.cell_detail, name='cell_detail'),
    path('<int:pk>/edit/', views.cell_update, name='cell_update'),
    path('<int:cell_pk>/report/add/', views.meeting_report_create, name='meeting_report_create'),
    path('<int:cell_pk>/calendar/add/', views.cell_event_create, name='cell_event_create'),
    path('<int:cell_pk>/calendar/events/', views.cell_events_json, name='cell_events_json'),
    path('consolidated/', views.consolidated_report_create, name='consolidated_report'),
]
