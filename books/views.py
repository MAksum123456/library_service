from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


@extend_schema(
    tags=["Books"],
    description="secure methods are available for all users, "
    "and CRUD operations can be performed by the admin",
)
class BookListView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
