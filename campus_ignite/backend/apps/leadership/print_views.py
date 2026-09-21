from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StudentAnchor


@login_required
def print_anchor_list(request):
    anchors = StudentAnchor.objects.filter(is_active=True).select_related('user').order_by('user__first_name')
    return render(request, 'print/anchor_list.html', {'anchors': anchors, 'total': anchors.count()})