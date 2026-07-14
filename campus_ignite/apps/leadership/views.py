from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from apps.accounts.decorators import role_required
from .models import LeadershipPosition, LeadershipAssignment
from .forms import LeadershipAssignmentForm


@login_required
def leadership_directory(request):
    year = date.today().year
    positions = LeadershipPosition.objects.prefetch_related(
        'assignments__leader', 'assignments__second_in_cmd'
    ).all()
    assignments = {
        a.position_id: a
        for a in LeadershipAssignment.objects.filter(is_active=True, year=year).select_related(
            'leader', 'second_in_cmd', 'position'
        )
    }
    return render(request, 'leadership/directory.html', {
        'positions': positions,
        'assignments': assignments,
        'year': year,
    })


@login_required
@role_required('admin', 'pastor')
def assign_leader(request, position_id):
    position = get_object_or_404(LeadershipPosition, pk=position_id)
    year = date.today().year
    assignment, _ = LeadershipAssignment.objects.get_or_create(
        position=position, year=year,
        defaults={'leader_id': request.user.id}
    )
    if request.method == 'POST':
        form = LeadershipAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, f'{position} leadership updated.')
            return redirect('leadership_directory')
    else:
        form = LeadershipAssignmentForm(instance=assignment)
    return render(request, 'leadership/assign_form.html', {
        'form': form, 'position': position
    })
