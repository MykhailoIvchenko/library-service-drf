from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date", "actual_return_date")


class BorrowingDetailsSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date", "actual_return_date")
