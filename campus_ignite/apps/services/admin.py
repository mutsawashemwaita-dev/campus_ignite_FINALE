from django.contrib import admin
from .models import ServiceRecord

@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'message_title', 'preacher', 'guest_preacher', 'head_count']
    list_filter = ['date']
    search_fields = ['message_title', 'guest_preacher']
