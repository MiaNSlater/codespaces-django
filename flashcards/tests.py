import json
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden
from flashcards.models import User, FlashcardSet

class UserListViewTest(TestCase):

    @classmethod
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

    @classmethod
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

    @classmethod
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

    @classmethod
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

class SetListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='testpassword')

        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Set",
            cards_id=1,
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=cls.user.id
        )
    
    def test_list_sets_found(self):
        url = reverse('list_sets')
        response = self.client.post(url, {'user_id': self.user.id})

        self.assertContains(response, self.flashcard_set.name)
        self.assertContains(response, self.flashcard_set.cards_id)
        self.assertContains(response, self.flashcard_set.created_at)
        self.assertContains(response, self.flashcard_set.updated_at)
        self.assertContains(response, self.flashcard_set.author_id)

    def test_list_sets_not_found(self):
        url = reverse('list_sets')
        response = self.client.post(url, {'user_id': 999})

        self.assertNotContains(response, "Set Name:")
        self.assertContains(response, "No Flashcard Set found by this user.")

class SearchSetByIdTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.set = FlashcardSet.objects.create(
            name="Test Set1",
            cards_id=2,
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=3
        )
    
    def test_search_set_found(self):
        url = reverse('search_set')
        response = self.client.post(url, {'set_id': self.flashcard_set.id})

        self.assertContains(response, self.flashcard_set.id)
        self.assertContains(response, self.flashcard_set.name)
        self.assertContains(response, self.flashcard_set.created_at)
        self.assertContains(response, self.flashcard_set.updated_at)
        self.assertContains(response, self.author_id)
        self.assertContains(response, self.cards_id)

    def test_search_set_not_found(self):
        url = reverse('search_set')
        response = self.client.post(url, {'set_id': 999})

        self.assertContains(response, "No flashcard set found with that Id.")
        self.assertNotContains(response, "ID:")
        self.assertNotContains(response, "Name:")
        self.assertNotContains(response, "Created:")
        self.assertNotContains(response, "Updated:")
        self.assertNotContains(response, "Author:")
    
class DeleteSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.set = FlashcardSet.objects.create(
            name="Test Set2",
            cards_id=1,
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=2
        )
    
    def test_delete_set_success(self):
        url = reverse('delete_set')
        response = self.client.post(url, {'set_id': self.flashcard_set.id})

        self.assertRedirects(response, 'success.html')

        self.assertEqual(FlashcardSet.objects.count(), 0)

    def test_delete_non_existent_set(self):
        url = reverse('delete_set')
        response = self.client.post(url, {'set_id': 999})

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot delete a non-existent set.")

        self.assertEqual(FlashcardSet.objects.count(), 1)
    
    def test_delete_invalid_set(self):
        url = reverse('delete_set')
        response = self.client.post(url, {'set_id': ''})

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot delete a non-existent set.")

        self.assertEqual(FlashcardSet.objects.count(), 1)

class CreateSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='testpassword')
    
    def test_create_flashcardset_success(self):
        url = reverse('create_flashcard_set')
        form_data = {
            'user_id': self.user.id,
            'set_name': 'testset'
        }

        response = self.client.post(url, form_data)
        self.assertRedirects(response, 'success.html')
        self.assertEqual(FlashcardSet.objects.count(), 1)

        flashcard_set = FlashcardSet.objects.first()
        self.assertEqual(flashcard_set.name, "Test Flashcard Set")
        self.assertEqual(flashcard_set.author, self.user)

    def test_create_flashcardset_invalid_user_id(self):
        url = reverse('create_flashcard_set')
         form_data = {
            'user_id': 999,
            'set_name': 'testset'
        }

        response = self.client.post(url, form_data)
        self.assertEqual(FlashcardSet.objects.count(), 0)
    
    def test_create_flashcardset_no_set_name(self):
        url = reverse('create_flashcard_set')
         form_data = {
            'user_id': self.user.id,
            'set_name': ''
        }

        response = self.client.post(url, form_data)
        self.assertEqual(FlashcardSet.objects.count(), 0)

    def test_create_flashcardset_no_user_id(self):
        url = reverse('create_flashcard_set')
         form_data = {
            'user_id': '',
            'set_name': 'testset'
        }

        response = self.client.post(url, form_data)
        self.assertEqual(FlashcardSet.objects.count(), 0)