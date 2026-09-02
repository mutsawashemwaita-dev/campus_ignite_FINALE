from django.contrib import admin
from .models import Department, DepartmentMember, DepartmentPost, DepartmentEvent

admin.site.register(Department)
admin.site.register(DepartmentMember)
admin.site.register(DepartmentPost)
admin.site.register(DepartmentEvent)