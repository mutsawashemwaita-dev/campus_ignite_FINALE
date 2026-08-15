from django.contrib import admin
from .models import Newbie

@admin.register(Newbie)
class NewbieAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'program', 'year_of_study', 'status', 'date_registered']
    list_filter  = ['status', 'year_of_study']
    search_fields= ['first_name', 'last_name', 'phone', 'program']
