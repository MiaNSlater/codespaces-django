#from django.http import JsonResponse
import json
from django.shortcuts import render, redirect
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

def submit_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        admin = request.POST.get('admin') == 'on'

        user_input = User(username = username, password = password, admin = admin)
        user_input.save()

        return redirect('success.html')
    return render(request, 'create_user.html')

def success(request):
    return render(request, 'success.html')