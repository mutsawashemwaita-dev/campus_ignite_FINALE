from django.urls import path
from . import views

urlpatterns = [
    path('', views.pastor_list, name='pastor_list'),
    path('add/', views.pastor_create, name='pastor_create'),
    path('<int:pk>/edit/', views.pastor_update, name='pastor_update'),
    path('<int:pk>/deactivate/', views.pastor_deactivate, name='pastor_deactivate'),
]
