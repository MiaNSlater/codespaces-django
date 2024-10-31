from django.db import models

class Flashcard(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    #difficulty = models.enums()