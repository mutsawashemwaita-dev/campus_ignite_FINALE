from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, Role
from apps.cells.models import Cell, CellType, CellMember


class CellsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.cell_leader_role = Role.objects.create(name=Role.CELL_LEADER)
        self.member_role = Role.objects.create(name=Role.LEADERSHIP)

        self.facilitator = CustomUser.objects.create_user(
            username='cell_facilitator',
            password='Password123!',
            first_name='Cell',
            last_name='Leader',
            role=self.cell_leader_role
        )

        self.other_user = CustomUser.objects.create_user(
            username='other_person',
            password='Password123!',
            first_name='Other',
            last_name='Person',
            role=self.member_role
        )

        self.cell_type = CellType.objects.create(name='Campus Cell')
        self.cell = Cell.objects.create(
            name='Alpha Cell',
            cell_type=self.cell_type,
            facilitator=self.facilitator,
            meeting_day='Wednesday',
            meeting_time='17:00:00'
        )

    def test_cell_leader_ids(self):
        self.assertEqual(self.cell.get_leader_ids(), [self.facilitator.id])

    def test_unauthorized_user_cannot_edit_cell(self):
        self.client.login(username='other_person', password='Password123!')
        response = self.client.get(reverse('cell_update', args=[self.cell.pk]), follow=True)
        self.assertRedirects(response, reverse('cell_detail', args=[self.cell.pk]))
        messages = list(response.context['messages'])
        self.assertTrue(any('permission' in str(m).lower() for m in messages))

    def test_facilitator_can_access_cell_edit(self):
        self.client.login(username='cell_facilitator', password='Password123!')
        response = self.client.get(reverse('cell_update', args=[self.cell.pk]))
        self.assertEqual(response.status_code, 200)

    def test_add_cell_member(self):
        self.client.login(username='cell_facilitator', password='Password123!')
        response = self.client.post(
            reverse('add_cell_member', args=[self.cell.pk]),
            {'member_search': 'other_person', 'attendance': 'consistent'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CellMember.objects.filter(cell=self.cell, user=self.other_user).exists())
