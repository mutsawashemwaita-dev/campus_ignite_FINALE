from django.urls import path
from . import views

urlpatterns = [
    path('login/',                       views.login_view,       name='login'),
    path('logout/',                      views.logout_view,      name='logout'),
    path('profile/',                     views.profile,          name='profile'),
    path('users/',                       views.user_list,        name='user_list'),
    path('users/add/',                   views.user_create,      name='user_create'),
    path('users/<int:pk>/edit/',         views.user_edit,        name='user_edit'),
    path('users/<int:pk>/deactivate/',   views.user_deactivate,  name='user_deactivate'),
    path('users/<int:pk>/activate/',     views.user_activate,    name='user_activate'),
]
