from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Newbie


@login_required
def newbie_list(request):
    status_filter = request.GET.get('status', '')
    newbies = Newbie.objects.select_related('registered_by').all()
    if status_filter:
        newbies = newbies.filter(status=status_filter)

    counts = {
        'total':     Newbie.objects.count(),
        'new':       Newbie.objects.filter(status='new').count(),
        'contacted': Newbie.objects.filter(status='contacted').count(),
        'following': Newbie.objects.filter(status='following').count(),
        'connected': Newbie.objects.filter(status='connected').count(),
    }
    return render(request, 'newbies/list.html', {
        'newbies': newbies,
        'counts': counts,
        'status_filter': status_filter,
    })


@login_required
def newbie_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        program    = request.POST.get('program', '').strip()
        year       = request.POST.get('year_of_study', 'Part 1')
        notes      = request.POST.get('notes', '').strip()

        if not first_name or not last_name or not phone or not program:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'newbies/register.html', {'post': request.POST})

        Newbie.objects.create(
            first_name    = first_name,
            last_name     = last_name,
            phone         = phone,
            program       = program,
            year_of_study = year,
            notes         = notes,
            registered_by = request.user,
        )
        messages.success(request, f'{first_name} {last_name} registered successfully!')
        return redirect('newbie_list')

    return render(request, 'newbies/register.html')


@login_required
def newbie_update_status(request, pk):
    newbie = get_object_or_404(Newbie, pk=pk)
    if request.method == 'POST':
        newbie.status = request.POST.get('status', newbie.status)
        newbie.notes  = request.POST.get('notes', newbie.notes)
        newbie.save()
        messages.success(request, f'{newbie.get_full_name()} status updated.')
    return redirect('newbie_list')


@login_required
def newbie_delete(request, pk):
    newbie = get_object_or_404(Newbie, pk=pk)
    name = newbie.get_full_name()
    newbie.delete()
    messages.success(request, f'{name} removed.')
    return redirect('newbie_list')