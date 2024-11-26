#from django.http import JsonResponse
import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from flashcards.models import User
from flashcards.models import Flashcard
from flashcards.models import FlashcardSet
from flashcards.models import Comment
from flashcards.models import Collection
from flashcards.models import DifficultyLevel

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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        admin = request.POST.get('admin') == 'on'

        if not username or not password:
             return HttpResponseForbidden("Forbidden: You cannot create a new user without a valid username or password.")

        user_input = User(username = username, password = password, admin = admin)
        user_input.save()

        return redirect('success')
    return render(request, 'create_user.html')

def create_flashcard_set(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        set_name = request.POST.get('set_name')
        ##author = get_object_or_404(User, id=user_id)

        if not user_id or not set_name:
             return HttpResponseForbidden("Forbidden: You cannot create a new set without a valid user id or set name.")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot create a new set without a valid user id or set name.")
            
        author = get_object_or_404(User, id=user_id)

        set_input = FlashcardSet(name=set_name, author=author)
        set_input.save()

        return redirect('success')
    return render(request, 'create_flashcard_set.html')

def create_collection(request):
    if request.method == 'POST':
        colname = request.POST.get('colname')
        user_id = request.POST.get('user_id')

        if not colname or not user_id:
            return HttpResponseForbidden("Forbidden: You cannot create a new collection without a Collection Name or an Author Id.")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden("Forbidden: Invalid User Id.")

        col_input = Collection(name=colname, author=user)
        col_input.save()

        return redirect('success')
    return render(request, 'create_collection.html')

def create_flashcards(request):
    reqset = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        if not set_id:
            return HttpResponseForbidden("Forbidden: Cannot add cards to a non-existent set.")

        try:
            reqset = FlashcardSet.objects.get(id=set_id)
        except FlashcardSet.DoesNotExist:
            return HttpResponseForbidden("Forbidden: Cannot add cards to a non-existent set.")
        
        if reqset:
            if 'add' in request.POST:
                question = request.POST.get('question')
                answer = request.POST.get('answer')
                difficulty = request.POST.get('difficulty')

                if not question or not answer or not difficulty:
                    return HttpResponseForbidden("Forbidden: Cannot create a new flashcard without a question, answer, or difficulty.")
                
                valid_difficulties = {choice[0]: choice[1] for choice in DifficultyLevel.choices}
                if difficulty not in valid_difficulties.keys() and difficulty not in valid_difficulties.values():
                    return HttpResponseForbidden("Forbidden: You must enter a valid difficulty.")
                
                card_input = Flashcard(question=question, answer=answer, difficulty=difficulty, flashcardset=reqset)
                card_input.save()
                
                return redirect('success')
    return render(request, 'create_flashcards.html', {'reqset': reqset})

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

        return redirect('success')
    return render(request, 'delete_user.html')

def delete_set(request):
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        try:
            set_to_delete = FlashcardSet.objects.get(id=set_id)
        except FlashcardSet.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot delete a non-existent set.")
            
        set_to_delete.delete()

        return redirect('success')
    return render(request, 'delete_set.html')

def delete_collection(request):
    if request.method == 'POST':
        col_id = request.POST.get('col_id')
        try:
            col_to_delete = Collection.objects.get(id=col_id)
        except Collection.DoesNotExist:
            return HttpResponseForbidden("Forbidden: You cannot delete a non-existent collection.")
            
        col_to_delete.delete()

        return redirect('success')
    return render(request, 'delete_collection.html')

def search_user(request):
    user = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponseForbidden("Forbidden: Cannot update a non-existent user.")
        
        if user:
            if 'update' in request.POST:
                user.username = request.POST.get('username', user.username)
                user.password = request.POST.get('password', user.password)

                user.save()

                return redirect('success')
    return render(request, 'update_user.html', {'user': user})

def update_set(request):
    reqset = None
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        if set_id:
            try:
                reqset = FlashcardSet.objects.get(id=set_id)
            except FlashcardSet.DoesNotExist:
                return HttpResponseForbidden("Forbidden: Cannot update a non-existent set.")
        
        if reqset:
            if 'update' in request.POST:
                reqset.name = request.POST.get('name', reqset.name)

                reqset.save()

                return redirect('success')
    return render(request, 'update_set.html', {'reqset': reqset})

def update_collection(request):
    reqcol = None
    if request.method == 'POST':
        col_id = request.POST.get('col_id')
        if col_id:
            try:
                reqcol = Collection.objects.get(id=col_id)
            except Collection.DoesNotExist:
                return HttpResponseForbidden("Forbidden: Cannot update a non-existent collection.")
        
        if reqcol:
            if 'update' in request.POST:
                reqcol.name = request.POST.get('name', reqcol.name)

                reqcol.save()

                return redirect('success')
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
        return redirect('success')
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

def random_collection(request):
    collections = Collection.objects.all()
    random_col = random.choice(collections) if collections else None
    return render(request, 'random_collection.html', {'collection': random_col})

def success(request):
    return render(request, 'success.html')