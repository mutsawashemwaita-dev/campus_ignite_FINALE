from django.contrib import admin
from .models import Department, DepartmentMember, DepartmentPost

admin.site.register(Department)
admin.site.register(DepartmentMember)
admin.site.register(DepartmentPost)
