from django.utils import timezone
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

        current_date = timezone.now()

        if self.borrow_date is not None:
            if self.expected_return_date < self.borrow_date:
                raise ValidationError("The expected return date cannot be before the borrow date")
            elif self.expected_return_date < current_date:
                raise ValidationError("The expected return date cannot be in the past.")

        if (self.actual_return_date is not None and
                self.actual_return_date < self.borrow_date):
            raise ValidationError("The actual return date cannot be before the borrow date")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.actual_return_date is None

    @property
    def user_id(self):
        return self.user.id

