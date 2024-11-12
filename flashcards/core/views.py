#from django.http import JsonResponse
import json
from django.shortcuts import render
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

def list_users(request):
    udata = list(User.objects.values('id', 'username', 'admin'))
    ujson_data = json.dumps(udata)
    return render(request, 'list_users.html', {'listuserdata_json': ujson_data})
    #uqueryset = User.objects.all().values('id', 'username', 'admin')
    #udata = list(uqueryset)
    #return JsonResponse(udata, safe=False)


#def list_users(request):
    #users = User.objects.all()
    #return render(request, 'list_users.html', {'users': users})

#def list_users(request):
  #  users = User.objects.all()
   # users_json = serialize('json', users)
   # return render(request, 'list_users.html', {'users_json': users_json})