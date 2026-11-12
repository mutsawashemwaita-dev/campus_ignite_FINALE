from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Department

# Re-exports for backwards compatibility
from apps.cells.print_views import print_cell_reports, print_consolidated_report
from apps.services.print_views import print_service, print_services_all
from apps.notifications.print_views import print_notifications


@login_required
def print_department(request, pk):
    dept    = get_object_or_404(Department, pk=pk)
    members = dept.members.select_related('user').all()
    posts   = dept.posts.select_related('posted_by').all()
    return render(request, 'print/department.html', {'dept': dept, 'members': members, 'posts': posts})
