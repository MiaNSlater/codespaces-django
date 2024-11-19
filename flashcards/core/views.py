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

def list_collections(request):
    collectionsets = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            collectionsets = Collection.objects.get(author_id=user_id)
        except Collection.DoesNotExist:
            collectionsets = None
    return render(request, 'list_collections.html', {'collectionsets': collectionsets})

def list_all_collections(request):
    collections = Collection.objects.all()
    return render(request, 'get_collections.html', {'collections': collections})

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

def search_col(request):
    collectionsets = None
    if request.method == 'POST':
        col_id = request.POST.get('col_id')
        try:
            collectionsets = Collection.objects.get(id=col_id)
        except Collection.DoesNotExist:
            collectionsets = None
    return render(request, 'collections_by_id.html', {'collectionsets': collectionsets})

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

def create_collection(request):
    if request.method == 'POST':
        colname = request.POST.get('colname')

        col_input = Collection(name=colname)
        col_input.save()

        return redirect('success.html')
    return render(request, 'create_collection.html')

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

def delete_collection(request):
    if request.method == 'POST':
        col_id = request.POST.get('col_id')
        try:
            col_to_delete = Collection.objects.get(id=col_id)
        except FlashcardSet.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot delete a non-existent collection.")
            
        col_to_delete.delete()

        return redirect('success.html')
    return render(request, 'delete_collection.html')

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

def update_collection(request):
    reqcol = None
    if request.method == 'POST':
        col_id = request.POST.get('col_id')
        if col_id:
            reqcol = Collection.objects.get(id=col_id)
        
        if reqcol:
            if 'update' in request.POST:
                reqcol.name = request.POST.get('name', reqcol.name)

                reqcol.save()

                return redirect('success.html')
    return render(request, 'update_collection.html', {'reqcol': reqcol})

def comment_set(request):
    reqset = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        comment = request.POST.get('comment')
        author = request.POST.get('author')

        if set_id and not comment and not author:
            reqset = get_object_or_404(FlashcardSet, id=set_id)
            return render(request, 'post_comment.html', {'reqset': reqset})

        elif set_id and comment and author:
            reqset = get_object_or_404(FlashcardSet, id=set_id)
            if not comment or not author:
                return HttpResponseForbidden("Forbidden. Cannot submit a new comment without a valid comment or author.")
            try:
                author_user = User.objects.get(id=author)
            except User.DoesNotExist:
                return HttpResponseForbidden("Forbidden. Cannot submit a new comment without a valid comment or author.")
            set_input = Comment(comment = comment, author = author_user, flashcardset_id = reqset.id)
            set_input.save()
        return redirect('success.html')
    return render(request, 'post_comment.html', {'reqset': reqset})

def search_flashcard(request):
    reqcard = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        try:
            reqcard = Flashcard.objects.get(flashcardset_id=set_id)
        except Flashcard.DoesNotExist:
            reqcard = None
    return render(request, 'get_flashcards.html', {'reqcard': reqcard})
        

def success(request):
    return render(request, 'success.html')