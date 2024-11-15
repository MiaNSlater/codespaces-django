from django.db import models

class DifficultyLevel(models.TextChoices):
        EASY = 'E', 'Easy'
        MEDIUM = 'M', 'Medium'
        HARD = 'H', 'Hard'

class Flashcard(models.Model):
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=1,
        choices=DifficultyLevel.choices,
        default=None,
        null=True,
        blank=True,
    ) 

class User(models.Model):
      username = models.CharField(max_length=100)
      admin = models.BooleanField(default=False)
      password = models.CharField(max_length=100, null=True)

      def __str__(self):
            return f"Id: {self.id}, Username: {self.username}, Admin: {self.admin}"


class Comment(models.Model):
      comment = models.CharField(max_length=200)
      author = models.ForeignKey(User, on_delete=models.CASCADE)
      flashcardset = models.ForeignKey(FlashcardSet, on_delete.models.CASCADE)

      def __str__(self):
            return f"Comment: {self.comment}"

class FlashcardSet(models.Model):
      name = models.CharField(max_length=100)
      cards = models.ForeignKey(Flashcard, default=None, null=True, blank=True, on_delete=models.CASCADE,related_name="sets")
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
      author = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

      def __str__(self):
            return f"Name: {self.name}, Cards: {self.cards}, Created: {self.created_at}, Updated: {self.updated_at}, Author: {self.author}"

class Collection(models.Model):
      comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
      set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
      author = models.ForeignKey(User, on_delete=models.CASCADE)