from django.db import transaction
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from user.serializers import UserSerializers


class BorrowSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializers(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class CreateBorrowSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = (
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

    def validate(self, data):
        book = data.get("book")
        if book.inventory < 1:
            raise serializers.ValidationError("No books left in inventory")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data.get("book")

        with transaction.atomic():
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ()

    def validate(self, data):
        if data.actual_return_date is not None:
            raise serializers.ValidationError(
                "You can't turn the book two times."
            )
        return data
