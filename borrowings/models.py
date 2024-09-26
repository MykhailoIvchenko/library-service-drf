from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.expected_return_date < self.borrow_date:
            raise ValidationError("The expected return date cannot be before the borrow date")

        if self.actual_return_date < self.borrow_date:
            raise ValidationError("The actual return date cannot be before the borrow date")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
