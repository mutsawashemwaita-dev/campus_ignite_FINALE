from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.department_list,   name='department_list'),
    path('birthdays/',                              views.birthday_list,     name='birthday_list'),
    path('add/',                                    views.department_create, name='department_create'),
    path('<int:pk>/',                               views.department_detail, name='department_detail'),
    path('<int:pk>/edit/',                          views.department_edit,   name='department_edit'),
    path('<int:pk>/members/add/',                   views.add_member,        name='dept_add_member'),
    path('<int:pk>/members/<int:member_pk>/remove/', views.remove_member,   name='dept_remove_member'),
    path('<int:pk>/posts/add/',                     views.post_create,       name='dept_post_create'),
    path('<int:pk>/posts/<int:post_pk>/delete/',    views.post_delete,       name='dept_post_delete'),
]
