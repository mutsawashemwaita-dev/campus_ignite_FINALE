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
    positions = LeadershipPosition.objects.all()
    assignments = {
        a.position_id: a
        for a in LeadershipAssignment.objects.filter(
            is_active=True, year=year
        ).select_related('leader', 'second_in_cmd', 'position')
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
    assignment = LeadershipAssignment.objects.filter(
        position=position, year=year
    ).first()

    if request.method == 'POST':
        form = LeadershipAssignmentForm(request.POST, assignment=assignment)
        if form.is_valid():
            leader = form.cleaned_data['leader_username']
            second = form.cleaned_data['second_in_cmd_username']
            is_active = form.cleaned_data['is_active']
            yr = form.cleaned_data['year']

            if assignment:
                assignment.leader = leader
                assignment.second_in_cmd = second
                assignment.is_active = is_active
                assignment.year = yr
                assignment.save()
            else:
                LeadershipAssignment.objects.create(
                    position=position,
                    leader=leader,
                    second_in_cmd=second,
                    is_active=is_active,
                    year=yr,
                )
            messages.success(request, f'{position} leadership updated.')
            return redirect('leadership_directory')
    else:
        form = LeadershipAssignmentForm(assignment=assignment)

    return render(request, 'leadership/assign_form.html', {
        'form': form, 'position': position
    })
