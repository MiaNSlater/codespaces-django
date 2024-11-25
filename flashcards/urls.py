"""
URL configuration for hello_world project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from flashcards.core import views as core_views

urlpatterns = [
    path("", core_views.index),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("userlist", core_views.list_users, name='list_users'),
    path("createuser", core_views.submit_form, name='submit_form'),
    path("success.html", core_views.success, name='success.html'),
    path("userbyid", core_views.search_id, name='search_id'),
    path("deleteuser", core_views.delete_user, name='delete_user'),
    path("updateuser", core_views.search_user, name='search_user'),
    path("flashcardsetsearch", core_views.list_sets, name='list_sets'),
    path("createsets", core_views.create_flashcard_set, name='create_flashcard_set'),
    path("setsbyid", core_views.search_set, name='search_set'),
    path("deleteset", core_views.delete_set, name='delete_set'),
    path("updateset", core_views.update_set, name='update_set'),
    path("postcomment", core_views.comment_set, name='comment_set'),
    path("getflashcards", core_views.search_flashcard, name='search_flashcard'),
    path("listcollections", core_views.list_collections, name='list_collections'),
    path("collectionsbyid", core_views.search_col, name='search_col'),
    path("updatecollections", core_views.update_collection, name='update_collection'),
    path("createcollections", core_views.create_collection, name='create_collection'),
    path("getallcollections", core_views.list_all_collections, name='list_all_collections'),
    path("deletecollection", core_views.delete_collection, name='delete_collection'),
    path("randomcollection", core_views.random_collection, name='random_collection'),
    path("createflashcards", core_views.create_flashcards, name='create_flashcards'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
