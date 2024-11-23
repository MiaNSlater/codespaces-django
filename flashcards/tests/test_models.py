from django.test import TestCase
from flashcards.models import User, FlashcardSet, Comment, Collection, Flashcard, DifficultyLevel

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

    def test_collection_name_max_length(self):
        max_length = self.collection._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)
    
    def test_collection_comment_relationship(self):
        collection = self.collection
        self.assertEqual(collection.comment.comment, "This is a test comment.")
    
    def test_collection_flashcardset_relationship(self):
        collection = self.collection
        self.assertEqual(collection.flashcardset.name, "Test Flashcard Set")
    
    def test_collection_author_relationship(self):
        collection = self.collection
        self.assertEqual(collection.author.username, "username1")
    
    def test_collection_flashcardset_on_delete_cascade(self):
        self.flashcard_set.delete()
        with self.assertRaises(Collection.DoesNotExist):
            Collection.objects.get(id=self.collection.id)
        
    def test_collection_comment_on_delete_cascade(self):
        self.comment.delete()
        with self.assertRaises(Collection.DoesNotExist):
            Collection.objects.get(id=self.collection.id)
        
    def test_collection_author_on_delete_cascade(self):
        self.user.delete()
        with self.assertRaises(Collection.DoesNotExist):
            Collection.objects.get(id=self.collection.id)
    
    def test_collection_without_optional_fields(self):
        collection = Collection.objects.create(name="No relations")
        self.assertEqual(collection.name, "No relations")
        self.assertIsNone(collection.comment)
        self.assertIsNone(collection.flashcardset)
        self.assertIsNone(collection.author)
    
class FlashcardModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="username1", admin=False, password="password1")
        cls.flashcard_set = FlashcardSet.objects.create(name="Test Flashcard Set", author=cls.user)
        cls.flashcard = Flashcard.objects.create(
            question="What is the capital of Japan?",
            answer="Tokyo",
            flashcardset=cls.flashcard_set,
            difficulty=DifficultyLevel.EASY
        )

    def test_flashcard_creation(self):
        flashcard = self.flashcard
        self.assertEqual(flashcard.question, "What is the capital of Japan?")
        self.assertEqual(flashcard.answer, "Tokyo")
        self.assertEqual(flashcard.flashcardset, self.flashcard_set)
        self.assertEqual(flashcard.difficulty, DifficultyLevel.EASY)
    
    def test_flashcard_str_method(self):
        flashcard = self.flashcard
        self.assertEqual(
            str(flashcard),
            f"Question: {flashcard.question}, Answer: {flashcard.answer}, Difficulty: {flashcard.difficulty}"
        )

    def test_flashcard_question_max_length(self):
        max_length = self.flashcard._meta.get_field('question').max_length
        self.assertEqual(max_length, 100)
    
    def test_flashcard_answer_max_length(self):
        max_length = self.flashcard._meta.get_field('answer').max_length
        self.assertEqual(max_length, 100)
    
    def test_flashcard_difficulty_choices(self):
        flashcard = Flashcard.objects.create(
            question="What is 'God' in Japanese?",
            answer="Kami",
            flashcardset=cls.flashcard_set,
            difficulty=DifficultyLevel.MEDIUM
        )
        self.assertEqual(flashcard.difficulty, DifficultyLevel.MEDIUM)

        flashcard = Flashcard.objects.create(
            question="What does は mean in a Japanese sentence?",
            answer="Topic marker particle",
            flashcardset=cls.flashcard_set,
            difficulty=DifficultyLevel.HARD
        )
        self.assertEqual(flashcard.difficulty, DifficultyLevel.HARD)

        with self.assertRaises(ValueError):
            Flashcard.objects.create(
            question="Invalid difficulty test?",
            answer="Error",
            flashcardset=cls.flashcard_set,
            difficulty="Z"
        )
    
    def test_flashcard_flashcardset_relationship(self):
        flashcard = self.flashcard
        self.assertEqual(flashcard.flashcardset.name, "Test Flashcard Set")
    
    def test_flashcard_flashcardset_on_delete_cascade(self):
        self.flashcard_set.delete()
        with self.assertRaises(Flashcard.DoesNotExist):
            Flashcard.objects.get(id=self.flashcard.id)
    
    def test_flashcard_without_flashcardset(self):
        flashcard = Flashcard.objects.create(
            question="Independent Question?",
            answer="Independent Answer",
            difficulty=DifficultyLevel.EASY
        )

        self.assertEqual(flashcard.question, "Independent Question?")
        self.assertEqual(flashcard.answer, "Independent Answer")
        self.assertEqual(flashcard.difficulty, DifficultyLevel.EASY)
        self.assertIsNone(flashcard.flashcardset)
    
    def test_flashcard_without_difficulty(self):
        flashcard = Flashcard.objects.create(
            question="Independent Question?",
            answer="Independent Answer",
            flashcardset=self.flashcard_set
        )

        self.assertIsNone(flashcard.difficulty)
