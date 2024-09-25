from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
