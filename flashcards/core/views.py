#from django.http import JsonResponse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
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

def list_sets(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            flashcard_sets = FlashcardSet.objects.filter(author_id=user_id)
        except FlashcardSet.DoesNotExist:
            flashcard_sets = None
    return render(request, 'flashcard_set_list.html', {'flashcard_sets': flashcard_sets})

def search_id(request):
    user = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
    return render(request, 'user_by_id.html', {'user': user})

def submit_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        admin = request.POST.get('admin') == 'on'

        user_input = User(username = username, password = password, admin = admin)
        user_input.save()

        return redirect('success.html')
    return render(request, 'create_user.html')

def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        try:
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot delete a non-existent user.")
        if user_to_delete.admin:
            return HttpResponseForbidden("Forbidden: You cannot delete an admin user. This attempt has been logged.")
        user_to_delete.delete()

        return redirect('success.html')
    return render(request, 'delete_user.html')

def search_user(request):
    user = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
        
        if user:
            if 'update' in request.POST:
                user.username = request.POST.get('username', user.username)
                user.password = request.POST.get('password', user.password)

                user.save()

                return redirect('success.html')
    return render(request, 'update_user.html', {'user': user})

def success(request):
    return render(request, 'success.html')