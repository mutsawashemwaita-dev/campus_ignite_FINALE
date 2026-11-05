from django.urls import path
from . import views

urlpatterns = [
    path('', views.evangelism_home, name='evangelism_home'),
    path('analytics/', views.evangelism_analytics, name='evangelism_analytics'),
    path('add/', views.recruit_add, name='recruit_add'),
    path('<int:pk>/delete/', views.recruit_delete, name='recruit_delete'),
]
