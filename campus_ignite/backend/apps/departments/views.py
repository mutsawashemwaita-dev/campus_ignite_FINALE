from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Department, DepartmentMember, DepartmentPost, DepartmentEvent
from .forms import DepartmentForm, DepartmentMemberForm, DepartmentPostForm, DepartmentEventForm, DepartmentNewMemberForm
from apps.notifications.utils import create_notification


def _can_manage_department(user, dept):
    """Admins, pastors and the chairperson can manage any department.
    Everyone else can only manage a department they lead, co-lead, or belong to."""
    if user.is_admin or user.is_pastor or user.is_chairperson:
        return True
    if dept.leader_id == user.id or dept.second_in_cmd_id == user.id:
        return True
    return DepartmentMember.objects.filter(department=dept, user=user).exists()


def _require_department_permission(request, dept):
    """Returns True if allowed. If not, adds an error message (caller must redirect)."""
    if _can_manage_department(request.user, dept):
        return True
    messages.error(request, "You don't have permission to manage this department.")
    return False


@login_required
def department_list(request):
    departments = Department.objects.filter(is_active=True).prefetch_related('members').select_related('leader', 'second_in_cmd')
    grouped = {}
    for d in departments:
        grouped.setdefault(d.get_dept_type_display(), []).append(d)
    return render(request, 'departments/list.html', {'departments': departments, 'grouped': grouped})


@login_required
def department_detail(request, pk):
    dept    = get_object_or_404(Department, pk=pk)
    members = dept.members.select_related('user').all()
    posts   = dept.posts.select_related('posted_by').all()
    events  = dept.events.filter(event_date__gte=__import__('datetime').date.today()).order_by('event_date')
    return render(request, 'departments/detail.html', {'dept': dept, 'members': members, 'posts': posts, 'events': events})


@login_required
def department_create(request):
    if not (request.user.is_admin or request.user.is_pastor or request.user.is_chairperson):
        messages.error(request, "Only admins, pastors, or the chairperson can create new departments.")
        return redirect('department_list')
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" created successfully.')
            return redirect('department_detail', pk=dept.pk)
    else:
        form = DepartmentForm()
    return render(request, 'departments/form.html', {'form': form, 'title': 'Create Department'})


@login_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save(instance=dept)

            # Sync matching LeadershipAssignment if this department maps to an annual position
            rev_map = {
                'choir': 'choir_leader',
                'marketing': 'marketing_leader',
                'hospitality': 'hospitality_leader',
                'evangelism': 'evangelism_leader',
                'prayer': 'prayer_leader',
            }
            pos_name = rev_map.get(dept.dept_type)
            if pos_name and dept.leader:
                from apps.leadership.models import LeadershipPosition, LeadershipAssignment
                from datetime import date
                pos = LeadershipPosition.objects.filter(name=pos_name).first()
                if pos:
                    LeadershipAssignment.objects.update_or_create(
                        position=pos,
                        year=date.today().year,
                        defaults={
                            'leader': dept.leader,
                            'second_in_cmd': dept.second_in_cmd,
                            'second_in_cmd_2': dept.second_in_cmd_2,
                            'is_active': dept.is_active,
                        }
                    )

            messages.success(request, f'"{dept.name}" updated.')
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentForm(initial={
            'name': dept.name, 'dept_type': dept.dept_type,
            'description': dept.description,
            'leader_username': dept.leader.username if dept.leader else '',
            'second_in_cmd_username': dept.second_in_cmd.username if dept.second_in_cmd else '',
            'second_in_cmd_2_username': dept.second_in_cmd_2.username if dept.second_in_cmd_2 else '',
        })
    return render(request, 'departments/form.html', {'form': form, 'title': f'Edit: {dept.name}', 'dept': dept})


@login_required
def add_member(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    if request.method == 'POST':
        form = DepartmentMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['member_username']
            role_in_dept = form.cleaned_data.get('role_in_dept', '')
            member, created = DepartmentMember.objects.get_or_create(
                department=dept, user=user,
                defaults={'role_in_dept': role_in_dept}
            )
            if created:
                messages.success(request, f'{user.get_full_name()} added to {dept.name}.')
            else:
                messages.warning(request, f'{user.get_full_name()} is already a member.')
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentMemberForm()
    return render(request, 'departments/add_member.html', {'form': form, 'dept': dept})


@login_required
def remove_member(request, pk, member_pk):
    dept   = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    member = get_object_or_404(DepartmentMember, pk=member_pk, department=dept)
    name   = member.user.get_full_name()
    member.delete()
    messages.success(request, f'{name} removed from {dept.name}.')
    return redirect('department_detail', pk=pk)


@login_required
def post_create(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    if request.method == 'POST':
        form = DepartmentPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.department = dept
            post.posted_by  = request.user
            post.save()
            messages.success(request, 'Post published.')
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentPostForm()
    return render(request, 'departments/post_form.html', {'form': form, 'dept': dept})


@login_required
def post_delete(request, pk, post_pk):
    dept = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    post = get_object_or_404(DepartmentPost, pk=post_pk, department=dept)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('department_detail', pk=pk)


# ── Hospitality Birthday Section ─────────────────────────────
@login_required
def birthday_list(request):
    """Shows all people with birthdays, auto-populated from anyone in the system."""
    import datetime
    from apps.accounts.models import CustomUser

    today      = datetime.date.today()
    this_month = today.month

    # Everyone with a birthday recorded
    all_people = CustomUser.objects.filter(
        is_active=True, birthday__isnull=False
    ).order_by('birthday__month', 'birthday__day').select_related('role')

    # Group: this month, upcoming (next 30 days), all
    this_month_bdays = []
    upcoming_bdays   = []
    all_bdays        = []

    for person in all_people:
        bd = person.birthday
        this_year_bd = bd.replace(year=today.year)
        if this_year_bd < today:
            this_year_bd = bd.replace(year=today.year + 1)
        days_away = (this_year_bd - today).days

        entry = {
            'person':    person,
            'birthday':  bd,
            'display':   bd.strftime('%d %B'),
            'days_away': days_away,
            'is_today':  bd.month == today.month and bd.day == today.day,
        }
        all_bdays.append(entry)
        if bd.month == this_month:
            this_month_bdays.append(entry)
        if 0 <= days_away <= 30:
            upcoming_bdays.append(entry)

    upcoming_bdays.sort(key=lambda x: x['days_away'])

    return render(request, 'departments/birthdays.html', {
        'this_month_bdays': this_month_bdays,
        'upcoming_bdays':   upcoming_bdays,
        'all_bdays':        all_bdays,
        'this_month_name':  today.strftime('%B'),
        'today':            today,
    })

@login_required
def department_event_create(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if not _require_department_permission(request, dept):
        return redirect('department_detail', pk=pk)
    if request.method == 'POST':
        form = DepartmentEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.department = dept
            event.created_by = request.user
            event.save()
            _notify_dept_of_event(event)
            messages.success(request, 'Event added to calendar. Department members have been notified.')
            return redirect('department_detail', pk=dept.pk)
    else:
        form = DepartmentEventForm()
    return render(request, 'departments/calendar_event_form.html', {'form': form, 'dept': dept})


def _notify_dept_of_event(event):
    """Notify the department leader, 2IC, and all members about a new department event."""
    msg = f"New event: '{event.title}' on {event.event_date} for {event.department.name}."

    notified_ids = set()

    for user in [event.department.leader, event.department.second_in_cmd]:
        if user and user.id not in notified_ids:
            create_notification(
                recipient=user,
                title=f"New Department Event – {event.department.name}",
                message=msg,
                source_type='department_event',
                source_id=event.pk,
            )
            notified_ids.add(user.id)

    for membership in event.department.members.select_related('user').all():
        if membership.user_id not in notified_ids:
            create_notification(
                recipient=membership.user,
                title=f"Department Calendar – {event.department.name}",
                message=msg,
                source_type='department_event',
                source_id=event.pk,
            )
            notified_ids.add(membership.user_id)



@login_required
@login_required
def create_new_member(request, pk=None):
    from .forms import manageable_departments
    user = request.user
    privileged = user.is_admin or user.is_pastor or user.is_chairperson
    if not privileged and not manageable_departments(user).exists():
        messages.error(request, "Only leaders can add new members.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = DepartmentNewMemberForm(request.POST, user=user)
        if form.is_valid():
            person = form.save()
            dept = form.cleaned_data.get('department')
            if dept:
                messages.success(request, f'{person.get_full_name()} was created and added to {dept.name}.')
                return redirect('department_detail', pk=dept.pk)
            messages.success(request, f'{person.get_full_name()} was added to the system.')
            return redirect('create_new_member')
    else:
        initial = {'department': pk} if pk else {}
        form = DepartmentNewMemberForm(user=user, initial=initial)
    return render(request, 'departments/new_member_form.html', {'form': form})