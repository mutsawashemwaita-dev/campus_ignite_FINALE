from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.newbie_list,          name='newbie_list'),
    path('register/',                 views.newbie_register,      name='newbie_register'),
    path('<int:pk>/status/',          views.newbie_update_status, name='newbie_update_status'),
    path('<int:pk>/delete/',          views.newbie_delete,        name='newbie_delete'),
]
