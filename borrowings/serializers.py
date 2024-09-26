from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
            "user_id"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        
        if request and not request.user.is_staff:
            self.fields.pop("user_id")


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date",
                  "expected_return_date", "actual_return_date", "user_id")


class BorrowingDetailsSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date",
                  "actual_return_date", "user_id")


class CreateBorrowingSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("book", "expected_return_date")

    def validate_book(self, value):
        if value.inventory <= 0:
            raise ValidationError("This book is not available for borrowing.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        borrowing = Borrowing.objects.create(user=user, **validated_data)
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        return borrowing
