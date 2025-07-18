from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.views import BookListView

app_name = "books"

router = DefaultRouter()


router.register("books", BookListView)
urlpatterns = [
    path("", include(router.urls)),
]
