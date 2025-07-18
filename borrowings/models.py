from django.conf import settings
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="book_borrowed"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_borrowed"
    )

    def __str__(self) -> str:
        return (f"{self.user.email} borrowed "
                f"{self.book.title} on {self.borrow_date}")
