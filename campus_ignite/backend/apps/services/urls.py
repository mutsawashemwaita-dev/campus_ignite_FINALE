from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('add/', views.service_create, name='service_create'),
    path('<int:pk>/', views.service_detail, name='service_detail'),

    # Download all service records as PDF
    path('pdf/', views.service_pdf, name='service_pdf'),
]