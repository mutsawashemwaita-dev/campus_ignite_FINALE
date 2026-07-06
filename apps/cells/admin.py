from django.contrib import admin
from .models import Cell, CellType, CellMeetingReport, CellEvent, ConsolidatedCellReport

@admin.register(CellType)
class CellTypeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['name', 'cell_type', 'facilitator', 'second_in_cmd', 'meeting_day', 'is_active']
    list_filter = ['cell_type', 'is_active', 'meeting_day']
    search_fields = ['name', 'facilitator__first_name', 'facilitator__last_name']

@admin.register(CellMeetingReport)
class CellMeetingReportAdmin(admin.ModelAdmin):
    list_display = ['cell', 'date', 'head_count', 'facilitated_by', 'submitted_at']
    list_filter = ['cell', 'date']

@admin.register(CellEvent)
class CellEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'cell', 'event_date', 'created_by']

@admin.register(ConsolidatedCellReport)
class ConsolidatedCellReportAdmin(admin.ModelAdmin):
    list_display = ['prepared_by', 'period_start', 'period_end', 'sent_to_pastors', 'submitted_at']
