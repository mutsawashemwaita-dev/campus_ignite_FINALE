from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from apps.accounts.decorators import role_required
from .models import LeadershipPosition, LeadershipAssignment, StudentAnchor
from .forms import LeadershipAssignmentForm, StudentAnchorForm


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
            second_2 = form.cleaned_data['second_in_cmd_2_username']
            is_active = form.cleaned_data['is_active']
            yr = form.cleaned_data['year']

            if assignment:
                assignment.leader = leader
                assignment.second_in_cmd = second
                assignment.second_in_cmd_2 = second_2
                assignment.is_active = is_active
                assignment.year = yr
                assignment.save()
            else:
                LeadershipAssignment.objects.create(
                    position=position,
                    leader=leader,
                    second_in_cmd=second,
                    second_in_cmd_2=second_2,
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


@login_required
def student_anchor_list(request):
    anchors = StudentAnchor.objects.filter(is_active=True).select_related('user')
    return render(request, 'leadership/anchor_list.html', {'anchors': anchors})


@login_required
@role_required('admin', 'pastor')
def student_anchor_add(request):
    if request.method == 'POST':
        form = StudentAnchorForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            anchor, created = StudentAnchor.objects.get_or_create(user=user, defaults={'is_active': True})
            if not created:
                anchor.is_active = True
                anchor.save()
            messages.success(request, f'{user.get_full_name()} added as a Student Anchor.')
            return redirect('student_anchor_list')
    else:
        form = StudentAnchorForm()
    return render(request, 'leadership/anchor_form.html', {'form': form})


@login_required
@role_required('admin', 'pastor')
def student_anchor_remove(request, pk):
    anchor = get_object_or_404(StudentAnchor, pk=pk)
    name = anchor.user.get_full_name()
    anchor.delete()
    messages.success(request, f'{name} removed from Student Anchors.')
    return redirect('student_anchor_list')
