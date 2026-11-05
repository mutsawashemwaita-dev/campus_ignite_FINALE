from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, Role
from apps.cells.models import Cell, CellType
from apps.evangelism.models import EvangelismCampaign, CampaignCellGoal, Recruit


class EvangelismTests(TestCase):
    def setUp(self):
        self.campaign1 = EvangelismCampaign.objects.create(
            name='Kingdom Builders',
            semester_label='Semester 1 · 2026',
            campus_goal=100,
            is_active=True
        )

        self.cell_type = CellType.objects.create(name='Campus Cell')
        self.facilitator = CustomUser.objects.create_user(
            username='evan_facilitator',
            password='Password123!',
            first_name='Cell',
            last_name='Leader'
        )
        self.cell = Cell.objects.create(
            name='Bethel Cell',
            cell_type=self.cell_type,
            facilitator=self.facilitator,
            meeting_day='Tuesday',
            meeting_time='18:00:00'
        )

    def test_single_active_campaign_invariant(self):
        # Creating a second active campaign should automatically switch the first one off
        campaign2 = EvangelismCampaign.objects.create(
            name='Harvest Time',
            semester_label='Semester 2 · 2026',
            campus_goal=150,
            is_active=True
        )
        self.campaign1.refresh_from_db()
        self.assertFalse(self.campaign1.is_active)
        self.assertTrue(campaign2.is_active)

    def test_recruit_counts_toward_goal(self):
        independent_recruit = Recruit.objects.create(
            campaign=self.campaign1,
            cell=self.cell,
            category=Recruit.INDEPENDENT,
            full_name='Alice Wonderland',
            phone='123456789'
        )
        consistent_recruit = Recruit.objects.create(
            campaign=self.campaign1,
            cell=self.cell,
            category=Recruit.CONSISTENT,
            full_name='Bob Existing',
            phone='987654321'
        )
        self.assertTrue(independent_recruit.counts_toward_goal)
        self.assertFalse(consistent_recruit.counts_toward_goal)
