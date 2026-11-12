from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from apps.accounts.models import CustomUser, Role
from apps.departments.models import Department
from apps.leadership.models import LeadershipPosition, LeadershipAssignment


class DepartmentSyncTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADMIN)

        self.admin_user = CustomUser.objects.create_user(
            username='dept_admin',
            password='Password123!',
            first_name='Dept',
            last_name='Admin',
            role=self.admin_role
        )

        self.choir_leader = CustomUser.objects.create_user(
            username='choir_lead',
            password='Password123!',
            first_name='Choir',
            last_name='Leader'
        )

        self.choir_2ic = CustomUser.objects.create_user(
            username='choir_second',
            password='Password123!',
            first_name='Choir',
            last_name='Second'
        )

        self.choir_dept = Department.objects.create(
            name='Choir Ministry',
            dept_type='choir',
            leader=self.choir_leader,
            second_in_cmd=self.choir_2ic
        )

        self.choir_pos = LeadershipPosition.objects.create(
            name='choir_leader',
            sort_order=5
        )

    def test_second_in_cmds_property(self):
        self.assertEqual(self.choir_dept.second_in_cmds, [self.choir_2ic])

    def test_assign_leader_syncs_to_department(self):
        self.client.login(username='dept_admin', password='Password123!')
        new_leader = CustomUser.objects.create_user(
            username='new_choir_lead',
            password='Password123!',
            first_name='New',
            last_name='Lead'
        )

        response = self.client.post(
            reverse('assign_leader', args=[self.choir_pos.pk]),
            {
                'leader_username': 'new_choir_lead',
                'second_in_cmd_username': 'choir_second',
                'second_in_cmd_2_username': '',
                'year': date.today().year,
                'is_active': True,
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Department leader should now be automatically updated to new_leader!
        self.choir_dept.refresh_from_db()
        self.assertEqual(self.choir_dept.leader, new_leader)

    def test_department_form_with_dropdown_and_choices(self):
        from apps.departments.forms import DepartmentForm
        form = DepartmentForm(data={
            'name': 'Media & Visuals',
            'dept_type': 'media',
            'description': 'Handles live streaming',
            'leader': self.admin_user.pk,
            'second_in_cmd': self.choir_leader.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)
        dept = form.save()
        self.assertEqual(dept.dept_type, 'media')
        self.assertEqual(dept.leader, self.admin_user)
        self.assertEqual(dept.second_in_cmd, self.choir_leader)

    def test_department_form_legacy_username_support(self):
        from apps.departments.forms import DepartmentForm
        form = DepartmentForm(data={
            'name': 'Prayer Ministry',
            'dept_type': 'prayer',
            'leader_username': 'dept_admin',
            'second_in_cmd_username': 'choir_lead',
        })
        self.assertTrue(form.is_valid(), form.errors)
        dept = form.save()
        self.assertEqual(dept.leader, self.admin_user)
        self.assertEqual(dept.second_in_cmd, self.choir_leader)
