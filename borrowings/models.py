from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book
from library_service import settings


class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(null=False)
    actual_return_date = models.DateTimeField(null=True, blank=True, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        if self.expected_return_date < self.borrow_date:
            raise ValidationError("The expected return date cannot be before the borrow date")

        if self.actual_return_date < self.borrow_date:
            raise ValidationError("The actual return date cannot be before the borrow date")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
