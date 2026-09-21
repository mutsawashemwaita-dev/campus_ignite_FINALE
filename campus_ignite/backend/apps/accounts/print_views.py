from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CustomUser


@login_required
def print_alumni_list(request):
    alumni = CustomUser.objects.filter(is_alumni=True, is_active=True).order_by('first_name', 'last_name')
    return render(request, 'print/alumni_list.html', {'alumni': alumni, 'total': alumni.count()})