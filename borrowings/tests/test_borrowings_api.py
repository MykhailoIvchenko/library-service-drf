from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from books.models import Book

from rest_framework.test import APIClient
from rest_framework import status

from datetime import datetime, timedelta

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingDetailsSerializer

BOOKS_URL = reverse("books:book-list")
BORROWINGS_URL = reverse("borrowings:borrowing-list")

book_payload = {
    "title": "Test Book",
    "author": "Test author",
    "cover": "HARD",
    "inventory": 5,
    "daily_fee": 1
}

expected_return_date = datetime.now() + timedelta(days=5)
expected_return_date_zone_aware = timezone.now() + timedelta(days=5)


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "SOFT",
        "inventory": 5,
        "daily_fee": 2.05
    }

    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        book = sample_book()

        borrowing_data = {
            "book": book.id,
            "expected_return_date": expected_return_date,
        }

        res = self.client.post(BORROWINGS_URL, borrowing_data)

        self.assertEqual(res.status_code, 201)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(borrowing.book.id, book.id)
        self.assertEqual(
            borrowing.expected_return_date.replace(tzinfo=None),
            expected_return_date
        )

    def test_create_borrowing_assigns_user(self):
        book = sample_book()
        borrowing_data = {
            "book": book.id,
            "expected_return_date": expected_return_date,
        }

        res = self.client.post(BORROWINGS_URL, borrowing_data)

        self.assertEqual(res.status_code, 201)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_decreases_inventory(self):
        book = sample_book()
        initial_inventory = book.inventory

        borrowing_data = {
            "book": book.id,
            "expected_return_date": expected_return_date,
        }

        res = self.client.post(BORROWINGS_URL, borrowing_data)

        self.assertEqual(res.status_code, 201)

        book.refresh_from_db()
        self.assertEqual(book.inventory, initial_inventory - 1)

    def test_list_borrowings(self):
        book = sample_book()

        borrowing_data = {
            "book": book.id,
            "expected_return_date": expected_return_date,
        }

        self.client.post(BORROWINGS_URL, borrowing_data)

        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for item in serializer.data:
            item.pop('user_id', None)

        self.assertEqual(serializer.data, res.data)

    def test_filter_borrowings_by_activeness(self):
        book = sample_book()

        first_borrowing = Borrowing.objects.create(
            book=book, expected_return_date=expected_return_date_zone_aware,
            user=self.user)
        second_borrowing = Borrowing.objects.create(
            book=book, expected_return_date=expected_return_date_zone_aware,
            user=self.user)
        second_borrowing.actual_return_date = second_borrowing.expected_return_date
        second_borrowing.save()

        res = self.client.get(BORROWINGS_URL, {"is_active": "true"})

        returned_ids = [item['id'] for item in res.data]

        self.assertIn(first_borrowing.id, returned_ids)
        self.assertNotIn(second_borrowing.id, returned_ids)

    def test_retrieve_borrowing_details(self):
        book = sample_book()

        borrowing = Borrowing.objects.create(
            book=book, expected_return_date=expected_return_date_zone_aware,
            user=self.user)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailsSerializer(borrowing)

        borrowing_data = serializer.data.copy()
        borrowing_data.pop("user_id")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, borrowing_data)

    def test_user_can_only_see_own_borrowings(self):
        book = sample_book()

        user_borrowing_res = self.client.post(BORROWINGS_URL, {
            "book": book.id,
            "expected_return_date": expected_return_date,
        })

        other_user = get_user_model().objects.create_user(
            "other@test.com",
            "testpass",
        )
        self.client.force_authenticate(other_user)

        self.client.post(BORROWINGS_URL, {
            "book": book.id,
            "expected_return_date": expected_return_date,
        })

        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWINGS_URL)

        user_borrowings_ids = [user_borrowing_res.data["id"]]
        returned_ids = [item["id"] for item in res.data]

        self.assertEqual(len(res.data), 1)
        self.assertEqual(returned_ids, user_borrowings_ids)

    def test_user_can_only_see_own_borrowing_details(self):
        book = sample_book()

        borrowing = Borrowing.objects.create(
            book=book, expected_return_date=expected_return_date,
            user=self.user)

        other_user = get_user_model().objects.create_user(
            "other@test.com",
            "testpass",
        )
        self.client.force_authenticate(other_user)

        other_borrowing = Borrowing.objects.create(
            book=book, expected_return_date=expected_return_date,
            user=other_user)

        self.client.force_authenticate(self.user)

        url = detail_url(other_borrowing.id)
        res = self.client.get(url)

        own_borrowing_url = detail_url(borrowing.id)
        own_borrowing_res = self.client.get(own_borrowing_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(own_borrowing_res.status_code, status.HTTP_200_OK)


class AdminBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.first_user = get_user_model().objects.create_user(
            "first_user@test.com", "testpass"
        )
        self.second_user = get_user_model().objects.create_user(
            "second_user@test.com", "testpass"
        )

        self.first_borrowing = Borrowing.objects.create(
            book=sample_book(),
            expected_return_date=expected_return_date_zone_aware,
            user=self.first_user
        )

        self.second_borrowing = Borrowing.objects.create(
            book=sample_book(),
            expected_return_date=expected_return_date_zone_aware,
            user=self.second_user
        )
        
        self.admin = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_see_all_borrowings(self):
        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_borrowings_by_user_id(self):
        res = self.client.get(BORROWINGS_URL, {"user_id": self.first_user.id})

        returned_ids = [item['id'] for item in res.data]

        self.assertIn(self.first_borrowing.id, returned_ids)
        self.assertNotIn(self.second_borrowing.id, returned_ids)

    def test_admin_can_see_any_borrowing_details(self):
        first_borrowing_url = detail_url(self.first_borrowing.id)
        first_borrowing_res = self.client.get(first_borrowing_url)

        self.assertEqual(first_borrowing_res.status_code, status.HTTP_200_OK)

        second_borrowing_url = detail_url(self.second_borrowing.id)
        second_borrowing_res = self.client.get(second_borrowing_url)

        self.assertEqual(second_borrowing_res.status_code, status.HTTP_200_OK)
