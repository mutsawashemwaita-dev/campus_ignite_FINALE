from django.contrib import admin
from .models import LeadershipPosition, LeadershipAssignment

@admin.register(LeadershipPosition)
class LeadershipPositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']

@admin.register(LeadershipAssignment)
class LeadershipAssignmentAdmin(admin.ModelAdmin):
    list_display = ['position', 'leader', 'second_in_cmd', 'year', 'is_active']
    list_filter = ['year', 'is_active']
