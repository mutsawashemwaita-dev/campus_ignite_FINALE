from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Department, DepartmentMember, DepartmentPost
from .forms import DepartmentForm, DepartmentMemberForm, DepartmentPostForm


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
    return render(request, 'departments/detail.html', {'dept': dept, 'members': members, 'posts': posts})


@login_required
def department_create(request):
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
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save(instance=dept)
            messages.success(request, f'"{dept.name}" updated.')
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentForm(initial={
            'name': dept.name, 'dept_type': dept.dept_type,
            'description': dept.description,
            'leader_username': dept.leader.username if dept.leader else '',
            'second_in_cmd_username': dept.second_in_cmd.username if dept.second_in_cmd else '',
        })
    return render(request, 'departments/form.html', {'form': form, 'title': f'Edit: {dept.name}', 'dept': dept})


@login_required
def add_member(request, pk):
    dept = get_object_or_404(Department, pk=pk)
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
    member = get_object_or_404(DepartmentMember, pk=member_pk, department=dept)
    name   = member.user.get_full_name()
    member.delete()
    messages.success(request, f'{name} removed from {dept.name}.')
    return redirect('department_detail', pk=pk)


@login_required
def post_create(request, pk):
    dept = get_object_or_404(Department, pk=pk)
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
    post = get_object_or_404(DepartmentPost, pk=post_pk, department=dept)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('department_detail', pk=pk)


import datetime

@login_required
def birthday_list(request):
    """
    Show all members with birthdays, grouped by month.
    Accessible from the Hospitality department.
    """
    from apps.accounts.models import Member
    from apps.cells.models import CellMember

    month_filter = request.GET.get('month', '')
    members_qs = Member.objects.filter(is_active=True, birthday__isnull=False).order_by('birthday__month', 'birthday__day')

    if month_filter:
        members_qs = members_qs.filter(birthday__month=int(month_filter))

    # Group by month
    grouped = {}
    MONTHS = ['January','February','March','April','May','June',
              'July','August','September','October','November','December']
    for m in members_qs:
        month_name = MONTHS[m.birthday.month - 1]
        grouped.setdefault(month_name, []).append(m)

    # This month's birthdays
    today = datetime.date.today()
    this_month = Member.objects.filter(
        is_active=True, birthday__month=today.month
    ).order_by('birthday__day')

    return render(request, 'departments/birthdays.html', {
        'grouped': grouped,
        'this_month': this_month,
        'today': today,
        'month_filter': month_filter,
        'months': [(str(i+1), m) for i, m in enumerate(MONTHS)],
    })


# ── Hospitality Birthday Section ─────────────────────────────
@login_required
def birthday_list(request):
    """All people with birthdays — for the Hospitality department."""
    from apps.accounts.models import CustomUser, MemberProfile
    import datetime

    today      = datetime.date.today()
    this_month = today.month

    # Get all users with birthdays
    users_with_bday = CustomUser.objects.filter(
        birthday__isnull=False, is_active=True
    ).order_by('birthday__month', 'birthday__day')

    # Get all member profiles with birthdays
    profiles_with_bday = MemberProfile.objects.filter(
        birthday__isnull=False
    ).order_by('birthday__month', 'birthday__day')

    # Build unified list
    everyone = []
    for u in users_with_bday:
        everyone.append({
            'name':      u.get_full_name(),
            'birthday':  u.birthday,
            'month':     u.birthday.month,
            'day':       u.birthday.day,
            'type':      'System User',
            'phone':     u.phone,
            'this_month': u.birthday.month == this_month,
            'today':     u.birthday.month == today.month and u.birthday.day == today.day,
        })
    for p in profiles_with_bday:
        # Don't double-count if linked to a user
        if not p.user_id:
            everyone.append({
                'name':      p.get_full_name(),
                'birthday':  p.birthday,
                'month':     p.birthday.month,
                'day':       p.birthday.day,
                'type':      'Member',
                'phone':     p.phone,
                'this_month': p.birthday.month == this_month,
                'today':     p.birthday.month == today.month and p.birthday.day == today.day,
            })

    # Sort by month then day
    everyone.sort(key=lambda x: (x['month'], x['day']))

    # Group by month
    months = {}
    import calendar
    for person in everyone:
        month_name = calendar.month_name[person['month']]
        months.setdefault(month_name, []).append(person)

    return render(request, 'departments/birthdays.html', {
        'months': months,
        'everyone': everyone,
        'this_month': calendar.month_name[this_month],
        'today': today,
        'today_birthdays': [p for p in everyone if p['today']],
        'this_month_birthdays': [p for p in everyone if p['this_month']],
    })


@login_required
def birthday_list(request):
    """Shows all people with birthdays, auto-populated from anyone in the system."""
    from apps.accounts.models import CustomUser
    import datetime

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
