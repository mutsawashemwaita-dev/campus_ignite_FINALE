import re
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from apps.cells.models import Cell
from .forms import RecruitForm
from .models import EvangelismCampaign, Recruit


def _active_campaign():
    return EvangelismCampaign.objects.filter(is_active=True).first()


def _is_evangelism_leader(user):
    """Leader or 2IC of the Evangelism department, or holder of the
    Evangelism Leader position in the Leadership directory this year."""
    from apps.departments.models import Department
    from apps.leadership.models import LeadershipAssignment

    in_department = Department.objects.filter(is_active=True).filter(
        Q(dept_type='evangelism') | Q(name__icontains='evangelism')
    ).filter(Q(leader=user) | Q(second_in_cmd=user)).exists()
    if in_department:
        return True
    return LeadershipAssignment.objects.filter(
        position__name='evangelism_leader', is_active=True, year=date.today().year,
    ).filter(Q(leader=user) | Q(second_in_cmd=user) | Q(second_in_cmd_2=user)).exists()


def _can_manage(user):
    """Evangelism leaders, pastors, admins and the chairperson."""
    return bool(user.is_admin or user.is_pastor or user.is_chairperson or _is_evangelism_leader(user))


def _logo_for(cell_name):
    """Logo shipped as a static file (img/cells/<cell-name>.jpeg), or '' if there isn't one."""
    slug = re.sub(r'[^a-z0-9]+', '-', cell_name.lower()).strip('-')
    for ext in ('jpeg', 'jpg', 'png'):
        path = f'img/cells/{slug}.{ext}'
        if finders.find(path):
            return static(path)
    return ''


def _pct(count, target):
    return min(int(count * 100 / target), 100) if target else 0


def _stats(campaign):
    counted = campaign.recruits.exclude(category=Recruit.CONSISTENT)
    per_cell = {row['cell']: row['n'] for row in counted.values('cell').annotate(n=Count('id'))}

    cells = []
    for goal in campaign.cell_goals.select_related('cell', 'cell__facilitator'):
        n = per_cell.get(goal.cell_id, 0)
        left = goal.target - n
        if n > goal.target:
            note = f'{n - goal.target} above the cell goal'
        elif n == goal.target:
            note = 'Cell goal reached — keep recruiting!'
        else:
            note = f'{left} more new member{"" if left == 1 else "s"} to reach this cell goal'
        cells.append({
            'name': goal.cell.name,
            'leader': goal.cell.facilitator.get_full_name() or goal.cell.facilitator.username,
            'logo': _logo_for(goal.cell.name),
            'count': n,
            'target': goal.target,
            'over': max(n - goal.target, 0),
            'pct': _pct(n, goal.target),
            'note': note,
        })
    cells.sort(key=lambda c: (-c['count'], c['name'].lower()))

    scoreboard = []
    rows = counted.values('added_by', 'added_by__first_name', 'added_by__last_name') \
                  .annotate(n=Count('id')).order_by('-n')
    for row in rows:
        full = f"{row['added_by__first_name'] or ''} {row['added_by__last_name'] or ''}".strip()
        if row['added_by'] is None or not full:
            full = 'Former member'
        initials = ''.join(part[0] for part in full.split()[:2]).upper()
        scoreboard.append({'name': full, 'initials': initials, 'count': row['n']})

    total = counted.count()
    return {
        'cells': cells,
        'total': total,
        'total_pct': _pct(total, campaign.campus_goal),
        'scoreboard': scoreboard,
    }


@login_required
def evangelism_home(request):
    campaign = _active_campaign()
    context = {'campaign': campaign}
    if campaign:
        context.update(_stats(campaign))
    return render(request, 'evangelism/home.html', context)


@login_required
def evangelism_analytics(request):
    campaign = _active_campaign()
    context = {'campaign': campaign, 'categories': Recruit.CATEGORY_CHOICES}
    if campaign:
        can_manage = _can_manage(request.user)
        q = request.GET.get('q', '').strip()
        type_filter = request.GET.get('type', 'all')

        records = campaign.recruits.select_related('cell', 'added_by')
        if not can_manage:
            # Phone numbers etc. are only visible to evangelism leaders, pastors,
            # admins and the chairperson. Everyone else sees only their own entries.
            records = records.filter(added_by=request.user)
        if type_filter in dict(Recruit.CATEGORY_CHOICES):
            records = records.filter(category=type_filter)
        if q:
            records = records.filter(
                Q(full_name__icontains=q) | Q(referral_name__icontains=q) | Q(phone__icontains=q)
                | Q(program__icontains=q) | Q(residency__icontains=q) | Q(cell__name__icontains=q)
                | Q(added_by__first_name__icontains=q) | Q(added_by__last_name__icontains=q)
            )

        context.update(_stats(campaign))
        context.update({
            'records': records,
            'q': q,
            'type_filter': type_filter,
            'can_manage': can_manage,
        })
    return render(request, 'evangelism/analytics.html', context)


@login_required
def recruit_add(request):
    campaign = _active_campaign()
    if not campaign:
        messages.error(request, 'There is no active evangelism campaign yet. Ask an admin to set one up.')
        return redirect('evangelism_home')

    if request.method == 'POST':
        form = RecruitForm(request.POST, campaign=campaign)
        if form.is_valid():
            recruit = form.save(commit=False)
            recruit.campaign = campaign
            recruit.added_by = request.user
            recruit.save()
            messages.success(request, f'{recruit.full_name} was saved.')
            return redirect('evangelism_home')
    else:
        own_cell = Cell.objects.filter(
            Q(facilitator=request.user) | Q(second_in_cmd=request.user),
            evangelism_goals__campaign=campaign,
        ).first()
        form = RecruitForm(campaign=campaign, initial={'cell': own_cell.pk} if own_cell else {})
    return render(request, 'evangelism/recruit_form.html', {'form': form, 'campaign': campaign})


@login_required
@require_POST
def recruit_delete(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Only evangelism leaders, pastors, admins and the chairperson can delete records.')
        return redirect('evangelism_analytics')
    recruit = get_object_or_404(Recruit, pk=pk)
    name = recruit.full_name
    recruit.delete()
    messages.success(request, f'{name} was removed.')
    return redirect('evangelism_analytics')
