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
