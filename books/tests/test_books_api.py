from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book

from rest_framework.test import APIClient
from rest_framework import status

from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "SOFT",
        "inventory": 1,
        "daily_fee": 2.05
    }

    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required_for_read(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_auth_required_for_actions(self):
        res = self.client.post(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.patch(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.put(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.delete(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_details(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Test Book",
            "author": "Test author",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 1
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
