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
    flashcard_sets = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            flashcard_sets = FlashcardSet.objects.get(author_id=user_id)
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

def search_set(request):
    reqset = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        try:
            reqset = FlashcardSet.objects.get(id=set_id)
        except FlashcardSet.DoesNotExist:
            reqset = None
    return render(request, 'sets_by_id.html', {'reqset': reqset})

def submit_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        admin = request.POST.get('admin') == 'on'

        user_input = User(username = username, password = password, admin = admin)
        user_input.save()

        return redirect('success.html')
    return render(request, 'create_user.html')

def create_flashcard_set(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        set_name = request.POST.get('set_name')
        author = get_object_or_404(User, id=user_id)

        set_input = FlashcardSet(name=set_name, author=author)
        set_input.save()

        return redirect('success.html')
    return render(request, 'create_flashcard_set.html')

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

def delete_set(request):
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        try:
            set_to_delete = FlashcardSet.objects.get(id=set_id)
        except FlashcardSet.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot delete a non-existent set.")
            
        set_to_delete.delete()

        return redirect('success.html')
    return render(request, 'delete_set.html')

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

def update_set(request):
    reqset = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        if set_id:
            reqset = FlashcardSet.objects.get(id=set_id)
        
        if reqset:
            if 'update' in request.POST:
                reqset.name = request.POST.get('name', reqset.name)

                reqset.save()

                return redirect('success.html')
    return render(request, 'update_set.html', {'reqset': reqset})

def comment_set(request):
    set_id = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        if not set_id:
            return HttpResponseForbidden("Forbidden. Cannot submit a new comment without a valid flashcard set id.")
        
        reqset = get_object_or_404(FlashcardSet, id=set_id)

        comment = request.POST.get('comment')
        author = request.POST.get('author')
        if not author or not comment:
            return HttpResponseForbidden("Forbidden. Cannot submit a new comment without a valid author or comment.")

        set_input = Comment(comment = comment, author = author, set_id = reqset)
        set_input.save()

        return redirect('success.html')
    return render(request, 'post_comment.html')
        

def success(request):
    return render(request, 'success.html')