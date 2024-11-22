from django.test import TestCase
from flashcards.models import User, FlashcardSet, Comment, Collection

class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="username1", admin=False, password="password1")
        cls.user2 = User.objects.create(username="username2", admin=True, password="password2")

    def test_user_creation(self):
        user = self.user1
        self.assertEqual(user.username, "username1")
        self.assertEqual(user.admin, False)
        self.assertEqual(user.password, "password1")

    def test_user_str_method(self):
        user = self.user1
        self.assertEqual(str(user), f"Id: {user.id}, Username: {user.username}, Admin: {user.admin}")

    def test_user_admin_field(self):
        user = self.user2
        self.assertTrue(user.admin)
        self.assertFalse(self.user1.admin)
    
    def test_user_password_field(self):
        user = self.user1
        self.assertEqual(user.password, "password1")

    def test_user_with_default_admin(self):
        user = User.objects.create(username="no_admin", password="password123")
        self.assertFalse(user.admin)

class FlashcardSetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="username1", admin=False, password="password1")
        cls.flashcard_set = FlashcardSet.objects.create(
            name="Test Flashcard Set",
            author=cls.user
        )

    def test_flashcardset_creation(self):
        flashcard_set = self.flashcard_set
        self.assertEqual(flashcard_set.name, "Test Flashcard Set")
        self.assertEqual(flashcard_set.author, self.user)
        self.assertIsNotNone(flashcard_set.created_at)
        self.assertIsNotNone(flashcard_set.updated_at)

    def test_flashcardset_str_method(self):
        flashcard_set = self.flashcard_set
        expected_str = (
            f"Name: {flashcard_set.name}, Created: {flashcard_set.created_at}"
            f"Updated: {flashcard_set.updated_at}, Author: {flashcard_set.author}"
        )

        self.assertEqual(str(flashcard_set), expected_str)
    
    def test_flashcardset_author_relationship(self):
        flashcard_set = self.flashcard_set
        self.assertEqual(flashcard_set.author.username, "username1")
        self.assertEqual(flashcard_set.author, self.user)

    def test_flashcardset_updated_at_field(self):
        flashcard_set = self.flashcard_set
        old_updated_at = flashcard_set.updated_at
        flashcard_set.name = "Updated Flashcard Set"
        flashcard_set.save()
        self.assertGreater(flashcard_set.updated_at, old_updated_at)

    def test_flashcardset_author_on_delete_cascade(self):
        self.user.delete()
        with self.assertRaises(FlashcardSet.DoesNotExist):
            FlashcardSet.objects.get(id=self.flashcard_set.id)
    
    def test_flashcardset_max_length(self):
        flashcard_set = FlashcardSet.objects.get(id=self.flashcard_set.id)
        max_length = flashcard_set._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)
    
class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="username1", admin=False, password="password1")
        cls.flashcard_set = FlashcardSet.objects.create(name="Test Flashcard Set", author=cls.user)
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )

    def test_comment_creation(self):
        comment = self.comment
        self.assertEqual(comment.comment, "This is a test comment.")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.flashcardset, self.flashcard_set)

    def test_comment_str_method(self):
        comment = self.comment
        self.assertEqual(str(comment), "Comment: This is a test comment.")

    def test_comment_author_relationship(self):
        comment = self.comment
        self.assertEqual(comment.author.username, "username1")
    
    def test_comment_flashcardset_relationship(self):
        comment = self.comment
        self.assertEqual(comment.flashcardset.name, "Test Flashcard Set")

    def test_comment_flashcardset_on_delete_cascade(self):
        self.flashcard_set.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment.id)
    
    def test_comment_author_on_delete_cascade(self):
        self.user.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment.id)
    
    def test_comment_max_length(self):
        comment = Comment.objects.get(id=self.comment.id)
        max_length = comment._meta.get_field('comment').max_length
        self.assertEqual(max_length, 200)

    def test_comment_without_flashcardset(self):
        comment_without_flashcardset = Comment.objects.create(
            comment="No flashcard set.",
            author=self.user
        )

        self.assertIsNone(comment_without_flashcardset.flashcardset)
    
    def test_comment_without_author(self):
        with self.assertRaises(IntegrityError):
            Comment.objects.create(comment="No author.", flashcardset=self.flashcard_set)

class CollectionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="username1", admin=False, password="password1")
        cls.flashcard_set = FlashcardSet.objects.create(name="Test Flashcard Set", author=cls.user)
        cls.comment = Comment.objects.create(
            comment="This is a test comment.",
            author=cls.user,
            flashcardset=cls.flashcard_set
        )
        cls.collection = Collection.objects.create(
            name="Test Collection",
            comment=cls.comment,
            flashcardset=cls.flashcard_set,
            author=cls.user
        )

    def test_collection_creation(self):
        collection = self.collection
        self.assertEqual(collection.name, "Test Collection")
        self.assertEqual(collection.comment, "This is a test comment.")
        self.assertEqual(collection.flashcardset, self.flashcard_set)
        self.assertEqual(collection.author, self.user)
    
    def test_collection_str_method(self):
        collection = self.collection
        self.assertEqual(str(collection), f"Collection Name: {collection.name}")
    
    