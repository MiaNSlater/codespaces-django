from django.db import models

class DifficultyLevel(models.TextChoices):
        EASY = 'E', 'Easy'
        MEDIUM = 'M', 'Medium'
        HARD = 'H', 'Hard'

class Flashcard(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    difficulty = models.CharField(
        max_length=1,
        choices=DifficultyLevel.choices,
        default=None,
        null=True,
        blank=True,
    )
    
class FlashcardSet(models.Model):
      name = models.CharField(max_length=200)
      cards = models.ManyToManyField(Flashcard, related_name="sets")
      created_at = models.DateTimeField()