import json
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden
from flashcards.models import User

class UserListViewTest(TestCase):
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user1", admin=True)
        cls.user2 = User.objects.create(username="user2", admin=False)
    def test_list_users_view(self):
        url = reverse('list_users')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_users.html')

        listuserdata_json = response.context['listuserdata_json']
        expected_json_data = [
            {'id': self.user1.id, 'username': 'user1', 'admin': True},
            {'id': self.user2.id, 'username': 'user2', 'admin': False}
        ]
        self.assertJSONEqual(listuserdata_json, json.dumps(expected_json_data))

        self.assertContains(response, 'const listUserData = JSON.parse')
        self.assertContains(response, '"username": "user1"')
        self.assertContains(response, '"admin": true')

        self.assertContains(response, 'Username: user1 | Admin?: true')
        self.assertContains(response, 'Username: user2 | Admin?: false')

class SearchUserByIdViewTest(TestCase):
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="jamesdoe")
        cls.user2 = User.objects.create(username="jeweldoe")

    def test_search_user_by_id_valid(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': self.user1.id})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_by_id.html')

        self.assertContains(response, f"ID: {self.user1.id}")
        self.assertContains(response, f"Name: {self.user1.username}")

    def test_search_user_by_id_invalid(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': 999})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_by_id.html')

        self.assertContains(response, "No user found with that Id.")
    
    def test_search_user_by_id_empty(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': ''})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_by_id.html')

        self.assertContains(response, "ID:")
        self.assertContains(response, "Name:")

    def test_search_user_by_id_csrf(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': self.user1.id})

        self.assertEqual(response.status_code, 403)
    
class DeleteUserViewTest(TestCase):
    def setUpTestData(cls):
        cls.noadminuser = User.object.create(username=noadmin, admin=False)
        cls.adminuser = User.object.create(username=admin, admin=True)
    
    def test_delete_non_admin_user(self):
        url = reverse('delete_user')
        data = {'id': self.noadminuser.id}

        response = self.client.post(url, data, follow=True)

        self.assertRedirects(response, 'success.html')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.noadminuser.id)
    
    def test_delete_admin_user(self):
        url = reverse('delete_user')
        data = {'id': self.adminuser.id}

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot delete an admin user.")

        admin_user = User.objects.get(id=self.admin_user.id)
        self.assertEqual(admin_user.username, 'admin')
    
    def test_delete_non_existent_user(self):
        url = reverse('delete_user')
        data = {'id': 999}

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot delete a non-existent user.")

class UpdateUserViewTest(TestCase):
    def setUpTestData(cls):
        cls.user = User.object.create(username=oldusername, password=oldpassword)
    
    def test_search_and_update_user(self):
        search_url = reverse('search_user')
        response = self.client.post(search_url, {'user_id': self.user.id}, follow=True)

        self.assertContains(response, f'value="{self.user.username}"')

        updated_username = 'newusername'
        updated_password = 'newpassword'
        update_data = {
            'user_id': self.user.id,
            'username': updated_username,
            'password': updated_password,
            'update': 'update'
        }
        response = self.client.post(search_url, update_data, follow=True)

        self.assertRedirects(response, 'success.html')

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, updated_username)
        self.assertEqual(self.user.password, updated_password)

    def test_search_and_update_non_existent_user(self):
        search_url = reverse('search_user')
        response = self.client.post(search_url, {'user_id': 999}, follow=True)
        self.assertNotContains(response, 'Update User Details:')
    
class CreateUserViewTest(TestCase):
    def test_create_new_user(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'admin': 'on',
        }

        url = reverse('submit_form')
        response = self.client.post(url, form_data, follow=True)

        self.assertRedirects(response, 'success.html')

        self.assertTrue(User.objects.filter(username='testuser').exists())

        user = User.objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.password, 'testpassword')
        self.assertTrue(user.admin)
    
    def test_create_non_admin_user(self):
        form_data = {
            'username': 'normaluser',
            'password': 'normalpassword',
        }

        url = reverse('submit_form')
        response = self.client.post(url, form_data, follow=True)

        self.assertRedirects(response, 'success.html')

        self.assertTrue(User.objects.filter(username='normaluser').exists())

        user = User.objects.get(username='normaluser')
        self.assertEqual(user.username, 'normaluser')
        self.assertEqual(user.password, 'normalpassword')
        self.assertFalse(user.admin)
