from django.contrib import admin
from .models import Pastor

@admin.register(Pastor)
class PastorAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date_appointed', 'is_active']
    list_filter = ['title', 'is_active']
