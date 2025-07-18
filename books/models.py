from django.db import models


class Book(models.Model):
    class CoverBook(models.TextChoices):
        HARD = ("Hard",)
        SOFT = ("Soft",)

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=10, choices=CoverBook.choices, default=CoverBook.HARD
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.title
