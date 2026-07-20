from django.urls import path
from . import views

urlpatterns = [
    path('', views.leadership_directory, name='leadership_directory'),
    path('<int:position_id>/assign/', views.assign_leader, name='assign_leader'),
]
