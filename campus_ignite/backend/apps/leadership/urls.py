from django.urls import path
from . import views

urlpatterns = [
    path('', views.leadership_directory, name='leadership_directory'),
    path('<int:position_id>/assign/', views.assign_leader, name='assign_leader'),
    path('anchors/', views.student_anchor_list, name='student_anchor_list'),
    path('anchors/add/', views.student_anchor_add, name='student_anchor_add'),
    path('anchors/<int:pk>/remove/', views.student_anchor_remove, name='student_anchor_remove'),
]