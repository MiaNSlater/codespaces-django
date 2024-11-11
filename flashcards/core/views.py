import json

from django.shortcuts import render
from django.core.serializers import serialize
from flashcards.models import User
from flashcards.models import Flashcard
from flashcards.models import FlashcardSet
from flashcards.models import Comment
from flashcards.models import Collection


def index(request):
    context = {
    "title": "Django example",
    }
    return render(request, "index.html", context)

#def list_users(request):
    #users = User.objects.all()
    #return render(request, 'list_users.html', {'users': users})

#def list_users(request):
  #  users = User.objects.all()
   # users_json = serialize('json', users)
   # return render(request, 'list_users.html', {'users_json': users_json})