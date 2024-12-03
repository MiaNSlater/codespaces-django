import json
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden
from flashcards.models import User, FlashcardSet, Comment, Collection, Flashcard, DifficultyLevel

class UserListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user1", password="password1", admin=True)
        cls.user2 = User.objects.create(username="user2", password="password2", admin=False)
    def test_list_users_view(self):
        url = reverse('list_users')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('user1', response.content.decode())
        self.assertIn('user2', response.content.decode())

class SearchUserByIdViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="jamesdoe", password="password1", admin=True)
        cls.user2 = User.objects.create(username="jeweldoe", password="password2", admin=False)

    def test_search_user_by_id_valid(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': self.user1.id})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_by_id.html')

        self.assertContains(response, self.user1.id)
        self.assertContains(response, self.user1.username)

    def test_search_user_by_id_invalid(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': 999})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_by_id.html')

        self.assertContains(response, "No user found with that Id.")
    

    def test_search_user_by_id_csrf(self):
        url = reverse('search_id')
        response = self.client.post(url, {'user_id': self.user1.id})

        self.assertEqual(response.status_code, 200)
    
class DeleteUserViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.noadminuser = User.objects.create(username="noadmin", password="noadminpassword", admin=False)
        cls.adminuser = User.objects.create(username="admin", password="adminpassword", admin=True)
    
    def test_delete_non_admin_user(self):
        url = reverse('delete_user')
        data = {'id': self.noadminuser.id}

        response = self.client.post(url, data, follow=True)

        self.assertRedirects(response, '/success')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.noadminuser.id)
    
    def test_delete_admin_user(self):
        url = reverse('delete_user')
        data = {'id': self.adminuser.id}

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: You cannot delete an admin user.")

        admin_user = User.objects.get(id=self.adminuser.id)
        self.assertEqual(admin_user.username, 'admin')
    
    def test_delete_non_existent_user(self):
        url = reverse('delete_user')
        data = {'id': 999}

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: You cannot delete a non-existent user.")

class UpdateUserViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="oldusername", password="oldpassword")
    
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

        self.assertRedirects(response, '/success')

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, updated_username)
        self.assertEqual(self.user.password, updated_password)

    def test_search_and_update_non_existent_user(self):
        search_url = reverse('search_user')
        response = self.client.post(search_url, {'user_id': 999}, follow=True)

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: Cannot update a non-existent user.")

        #self.assertNotContains(response, 'Update User Details:')
    
class CreateUserViewTest(TestCase):
    def test_create_new_user(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'admin': 'on',
        }

        url = reverse('submit_form')
        response = self.client.post(url, form_data, follow=True)

        self.assertRedirects(response, '/success')

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

        self.assertRedirects(response, '/success')

        self.assertTrue(User.objects.filter(username='normaluser').exists())

        user = User.objects.get(username='normaluser')
        self.assertEqual(user.username, 'normaluser')
        self.assertEqual(user.password, 'normalpassword')
        self.assertFalse(user.admin)

    def test_create_empty_user(self):
        form_data = {
            'password': 'normalpassword'
        }

        url = reverse('submit_form')
        response = self.client.post(url, form_data, follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot create a new user without a valid username or password.", status_code=403)
        self.assertEqual(User.objects.count(), 0)

    def test_create_empty_password(self):
        form_data = {
            'username': 'normalusername'
        }

        url = reverse('submit_form')
        response = self.client.post(url, form_data, follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 0)

class SetListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='testpassword')
        #cls.card = Flashcard.objects.create(question='What is 4 x 5?', answer='20', difficulty='Easy')
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Set",
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=cls.user.id
        )
    
    def test_list_sets_found(self):
        url = reverse('list_sets')
        response = self.client.post(url, {'user_id': self.user.id})

        self.assertContains(response, self.flashcard_set.name)
        #self.assertContains(response, self.flashcard.name)
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
        cls.user = User.objects.create(username='testuser', password='testpassword', admin=False)
        #cls.card = Flashcard.objects.create(question='What is 4 x 5?', answer='20', difficulty='Easy')
        cls.set = FlashcardSet.objects.create(
            name="Test Set1",
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=cls.user.id
        )
    
    def test_search_set_found(self):
        url = reverse('search_set')
        response = self.client.post(url, {'set_id': self.set.id})

        formatted_created_at = self.set.created_at.strftime('%Y-%m-%d %H:%M:%S')
        formatted_updated_at = self.set.updated_at.strftime('%Y-%m-%d %H:%M:%S')

        self.assertContains(response, self.set.id)
        self.assertContains(response, self.set.name)
        self.assertContains(response, formatted_created_at)
        self.assertContains(response, formatted_updated_at)
        self.assertContains(response, self.author_id)

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
        cls.user = User.objects.create(username='testuser', password='testpassword', admin=False)
        #cls.card = Flashcard.objects.create(question='What is 4 x 5?', answer='20', difficulty='Easy')
        cls.set = FlashcardSet.objects.create(
            name="Test Set2",
            created_at="2024-01-01",
            updated_at="2024-01-02",
            author_id=cls.user.id
        )
    
    def test_delete_set_success(self):
        url = reverse('delete_set')
        response = self.client.post(url, {'set_id': self.set.id})

        self.assertRedirects(response, '/success')

        self.assertEqual(FlashcardSet.objects.count(), 0)

    def test_delete_non_existent_set(self):
        url = reverse('delete_set')
        response = self.client.post(url, {'set_id': 999})

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: You cannot delete a non-existent set.")

        self.assertEqual(FlashcardSet.objects.count(), 1)

class UpdateSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='testpassword')
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Original Name",
            author=cls.user
        )
    
    def test_update_flashcardset_success(self):
        url = reverse('update_set')
        form_data = {
            'set_id': self.flashcard_set.id,
            'name': 'Updated Name',
            'update': 'Update'
        }

        response = self.client.post(url, form_data)

        self.assertRedirects(response, '/success')

        self.flashcard_set.refresh_from_db()
        self.assertEqual(self.flashcard_set.name, "Updated Name")
    
    def test_update_flashcardset_invalid_id(self):
        url = reverse('update_set')
        invalid_set_id = 999
        form_data = {
            'set_id': invalid_set_id,
            'name': 'Updated Name',
            'update': 'Update'
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: Cannot update a non-existent set.")

        self.flashcard_set.refresh_from_db()
        self.assertEqual(self.flashcard_set.name, "Original Name")
    
    def test_update_flashcardset_missing_name(self):
        url = reverse('update_set')
        form_data = {
            'set_id': self.flashcard_set.id,
            'update': 'Update'
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 302)

        self.flashcard_set.refresh_from_db()
        self.assertEqual(self.flashcard_set.name, "Original Name")
    

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
        self.assertEqual(FlashcardSet.objects.count(), 1)

        flashcard_set = FlashcardSet.objects.first()
        self.assertEqual(flashcard_set.name, "testset")
        self.assertEqual(flashcard_set.author, self.user)

        self.assertRedirects(response, '/success')

    def test_create_flashcardset_invalid_user_id(self):
        url = reverse('create_flashcard_set')
        form_data = {
            'user_id': 999,
            'set_name': 'testset'
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot create a new set without a valid user id or set name.", status_code=403)
        self.assertEqual(FlashcardSet.objects.count(), 0)
    
    def test_create_flashcardset_no_set_name(self):
        url = reverse('create_flashcard_set')
        form_data = {
            'user_id': self.user.id
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot create a new set without a valid user id or set name.", status_code=403)
        self.assertEqual(FlashcardSet.objects.count(), 0)

class PostCommentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )

    def test_search_flashcard_set(self):
        url = reverse('comment_set')
        form_data = {
            'set_id': self.flashcard_set.id
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flashcard_set.id)

    def test_add_valid_comment(self):
        url = reverse('comment_set')
        form_data = {
            'set_id': self.flashcard_set.id,
            'comment': "This is a test comment.",
            'author': self.user.id
        }

        response = self.client.post(url, form_data)

        self.assertRedirects(response, '/success')

        comment = Comment.objects.get(flashcardset_id=self.flashcard_set.id)
        self.assertEqual(comment.comment, "This is a test comment.")
        self.assertEqual(comment.author, self.user)
    
    def test_add_comment_missing_comment(self):
        url = reverse('comment_set')
        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'comment': '',
            'author': self.user.id
        }

        response = self.client.post(url, {**form_data, 'post': ''}, follow=False)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.content.decode())
        print("Form data:", form_data)
        self.assertEqual(response.status_code, 403)

        self.assertFalse(Comment.objects.filter(flashcardset_id=self.flashcard_set.id).exists())

    def test_add_comment_invalid_author(self):
        url = reverse('comment_set')
        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'comment': "This is a test comment.",
            'author': 999
        }

        response = self.client.post(url, {**form_data, 'post': ''}, follow=False)
        self.assertEqual(response.status_code, 403)

        self.assertFalse(Comment.objects.filter(flashcardset_id=self.flashcard_set.id).exists())

class CollectionListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            flashcardset=cls.flashcard_set,
            author=cls.user,
            comment=cls.comment
        )
    
    def test_list_all_collections(self):
        url = reverse('list_all_collections')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Test Collection")
        self.assertContains(response, "Test Flashcard Set")
        self.assertContains(response, "testuser")
        self.assertContains(response, "This is a test comment.")
    
    def test_no_collections(self):
        Collection.objects.all().delete()

        url = reverse('list_all_collections')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "No collections found.")

class SearchCollectionByColIdTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            flashcardset=cls.flashcard_set,
            author=cls.user,
            comment=cls.comment
        )

    def test_list_collections_by_id_valid(self):
        url = reverse('search_col')
        response = self.client.post(url, data={'col_id': self.collection.id})

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Collection ID:")
        self.assertContains(response, f"{self.collection.id}")
        self.assertContains(response, "Test Flashcard Set")
        self.assertContains(response, "testuser")
        self.assertContains(response, "This is a test comment.")

    def test_list_collections_by_id_invalid(self):
        url = reverse('search_col')
        response = self.client.post(url, data={'col_id': 999})

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "No flashcard collection found with that Id.")

    def test_list_collections_by_id_none(self):
        url = reverse('search_col')
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, "Collection ID:")
        self.assertContains(response, "No flashcard collection found with that Id.")
    
class SearchCollectionByUserIdTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.otheruser = User.objects.create(username="othertestuser", password="othertestpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            flashcardset=cls.flashcard_set,
            author=cls.user,
            comment=cls.comment
        )
    
    def test_collection_search_user_id_valid(self):
        url = reverse('list_collections')
        response = self.client.post(url, data={'user_id': self.user.id})

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Collection ID:")
        self.assertContains(response, f"{self.collection.id}")
        self.assertContains(response, "Test Flashcard Set")
        self.assertContains(response, "testuser")
        self.assertContains(response, "This is a test comment.")
    
    def test_collection_search_user_id_invalid(self):
        url = reverse('list_collections')
        response = self.client.post(url, data={'user_id': self.otheruser.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Flashcard Collection found by this user.")
    
    def test_collection_search_user_id_none(self):
        url = reverse('list_collections')
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, "Collection ID:")
        self.assertContains(response, "No Flashcard Collection found by this user.")

class DeleteCollectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            flashcardset=cls.flashcard_set,
            author=cls.user,
            comment=cls.comment
        )
    
    def test_delete_collection_valid_id(self):
        url = reverse('delete_collection')
        response = self.client.post(url, data={'col_id': self.collection.id})

        self.assertRedirects(response, '/success')

        self.assertEqual(Collection.objects.count(), 0)

    def test_delete_collection_invalid_id(self):
        url = reverse('delete_collection')
        response = self.client.post(url, data={'col_id': 999})

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: You cannot delete a non-existent collection.")
    
    def test_delete_collection_get_request(self):
        url = reverse('delete_collection')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Collection.objects.filter(id=self.collection.id).exists())

class UpdateCollectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            flashcardset=cls.flashcard_set,
            author=cls.user,
            comment=cls.comment
        )
    
    def test_update_collection_valid_id(self):
        url = reverse('update_collection')
        form_data = {
            'col_id': self.collection.id,
            'name': "Updated Collection Name",
            'update': 'Update'
        }

        response = self.client.post(url, form_data)
        self.assertRedirects(response, '/success')

        self.collection.refresh_from_db()
        self.assertEqual(self.collection.name, "Updated Collection Name")
    
    def test_update_collection_invalid_id(self):
        url = reverse('update_collection')
        form_data = {
            'col_id': 999,
            'name': "Updated Collection Name",
            'update': 'Update'
        }
        
        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        #self.assertContains(response, "Forbidden: You cannot update a non-existent collection.")

        self.assertNotEqual(Collection.objects.count(), 0)
    
    def test_update_collection_get_request(self):
        url = reverse('update_collection')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.collection.refresh_from_db()
        self.assertEqual(self.collection.name, "Test Collection")

class CreateCollectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword")

    def test_create_collection_valid(self):
        url = reverse('create_collection')
        form_data = {
            'colname': 'New Collection',
            'user_id': self.user.id
        }

        response = self.client.post(url, form_data)

        collection = Collection.objects.get(name='New Collection')
        self.assertEqual(collection.name, 'New Collection')
        self.assertEqual(collection.author.id, self.user.id)

        self.assertRedirects(response, '/success')
    
    def test_create_collection_missing_name(self):
        url = reverse('create_collection')
        form_data = {
            'user_id': self.user.id
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: You cannot create a new collection without a Collection Name or an Author Id.", status_code=403)


    def test_create_collection_invalid_user_id(self):
        url = reverse('create_collection')
        form_data = {
            'colname': 'New Collection',
            'user_id': 999
        }

        response = self.client.post(url, form_data)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Forbidden: Invalid User Id.", status_code=403)
    
class RandomCollectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="testuser1", password="testpassword1")
        cls.flashcardset1 = FlashcardSet.objects.create(
            name="Flashcard Set 1", author=cls.user1
        )
        cls.comment1 = Comment.objects.create(
            comment="This is a test comment", 
            author=cls.user1, 
            flashcardset=cls.flashcardset1
        )
        cls.collection1 = Collection.objects.create(
            name="Collection 1",
            comment=cls.comment1,
            flashcardset=cls.flashcardset1,
            author=cls.user1
        )

    def test_random_collection_with_collections(self):
        url = reverse('random_collection')
        response = self.client.get(url)

        self.assertContains(response, "Collection Name:")
        self.assertContains(response, "Collection Set:")
        self.assertContains(response, "Collection Author:")
        self.assertContains(response, "Collection Comments:")

        self.assertContains(response, self.collection1.name)
        self.assertContains(response, self.collection1.flashcardset.name)
        self.assertContains(response, self.collection1.author.username)
        self.assertContains(response, self.collection1.comment.comment)
    
    def test_random_collection_no_collections(self):
        Collection.objects.all().delete()

        url = reverse('random_collection')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'random_collection.html')
        self.assertContains(response, "<p>No Collections found.</p>")

class CreateFlashcardTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="testpassword", admin=False)
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set", author=cls.user
        )
    
    def test_create_flashcard_success(self):
        url = reverse('create_flashcards')

        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)

        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'question': 'What language does Django use?',
            'answer': 'Python',
            'difficulty': 'Easy'
        }

        response = self.client.post(url, {**form_data, 'add': ''}, follow=False)
        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, '/success')

        flashcard = Flashcard.objects.get(question='What language does Django use?')
        self.assertEqual(flashcard.question, 'What language does Django use?')
        self.assertEqual(flashcard.answer, 'Python')
        self.assertEqual(flashcard.difficulty, 'Easy')
    
    def test_create_flashcard_invalid_difficulty(self):
        url = reverse('create_flashcards')
        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'question': 'What language does Django use?',
            'answer': 'Python',
            'difficulty': 'Xenu'
        }

        response = self.client.post(url, {**form_data, 'add': ''}, follow=False)
        self.assertEqual(response.status_code, 403)
    
    def test_create_flashcard_missing_question(self):
        url = reverse('create_flashcards')
        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'answer': 'Python',
            'difficulty': 'Easy'
        }

        response = self.client.post(url, {**form_data, 'add': ''}, follow=False)
        self.assertEqual(response.status_code, 403)
    
    def test_create_flashcard_missing_answer(self):
        url = reverse('create_flashcards')
        response = self.client.post(url, {'set_id': self.flashcard_set.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'set_id': self.flashcard_set.id,
            'question': 'What language does Django use?',
            'difficulty': 'Easy'
        }

        response = self.client.post(url, {**form_data, 'add': ''}, follow=False)
        self.assertEqual(response.status_code, 403)

    def test_create_flashcard_invalid_set(self):
        url = reverse('create_flashcards')
        form_data = {
            'set_id': 999,
            'question': 'What language does Django use?',
            'answer': 'Python',
            'difficulty': 'Easy'
        }

        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 403)
    