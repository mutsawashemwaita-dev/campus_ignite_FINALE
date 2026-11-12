from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, Role


class AccountsModelTests(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.pastor_role = Role.objects.create(name=Role.PASTOR)
        self.leader_role = Role.objects.create(name=Role.LEADERSHIP)

    def test_custom_user_roles(self):
        admin_user = CustomUser.objects.create(
            username='admin_john',
            first_name='John',
            last_name='Doe',
            role=self.admin_role
        )
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(admin_user.is_pastor)
        self.assertEqual(str(admin_user), "John Doe (Administrator)")

    def test_member_only_record(self):
        member = CustomUser.objects.create(
            username='member_xyz123',
            first_name='Jane',
            last_name='Smith'
        )
        member.set_unusable_password()
        member.save()
        self.assertTrue(member.is_member_only)
        self.assertEqual(str(member), "Jane Smith (Member)")

    def test_manager_login_users_and_member_attendees(self):
        login_u = CustomUser.objects.create_user(
            username='leader_mark',
            password='Password123!',
            first_name='Mark',
            last_name='Leader',
            role=self.leader_role
        )
        attendee = CustomUser.objects.create(
            username='member_abc999',
            first_name='Grace',
            last_name='Attendee',
        )
        attendee.set_unusable_password()
        attendee.save()

        login_users = list(CustomUser.objects.login_users())
        attendees = list(CustomUser.objects.member_attendees())

        self.assertIn(login_u, login_users)
        self.assertNotIn(attendee, login_users)
        self.assertIn(attendee, attendees)
        self.assertNotIn(login_u, attendees)

    def test_promote_member_to_login_user(self):
        from apps.accounts.forms import EditPersonForm
        attendee = CustomUser.objects.create(
            username='member_temp123',
            first_name='Peter',
            last_name='Promote',
        )
        attendee.set_unusable_password()
        attendee.save()
        self.assertTrue(attendee.is_member_only)

        form = EditPersonForm(
            data={
                'first_name': 'Peter',
                'last_name': 'Promote',
                'username': 'peter_leader',
                'new_password': 'NewPassword123!',
                'role_name': 'cell_leader',
            },
            instance=attendee
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()

        self.assertEqual(updated.username, 'peter_leader')
        self.assertFalse(updated.is_member_only)
        self.assertTrue(updated.has_usable_password())
        self.assertEqual(updated.role.name, Role.CELL_LEADER)


class AccountsAuthorizationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.leader_role = Role.objects.create(name=Role.LEADERSHIP)

        self.admin_user = CustomUser.objects.create_user(
            username='admin_user',
            password='Password123!',
            first_name='Admin',
            last_name='User',
            role=self.admin_role
        )

        self.regular_user = CustomUser.objects.create_user(
            username='regular_user',
            password='Password123!',
            first_name='Regular',
            last_name='User',
            role=self.leader_role
        )

    def test_unauthenticated_access_redirects(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_regular_user_blocked_from_user_list(self):
        self.client.login(username='regular_user', password='Password123!')
        response = self.client.get(reverse('user_list'), follow=True)
        # Should redirect to dashboard with error message
        self.assertRedirects(response, reverse('dashboard'))
        messages = list(response.context['messages'])
        self.assertTrue(any('permission' in str(m).lower() for m in messages))

    def test_admin_allowed_on_user_list(self):
        self.client.login(username='admin_user', password='Password123!')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
