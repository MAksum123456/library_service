from datetime import timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.utils import timezone


from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()


class BorrowingViewSet(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", password="password123"
        )
        self.staff_user = User.objects.create_user(
            email="staff@gmail.com",
            password="password123",
            is_staff=True,
        )
        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            inventory=3,
            daily_fee=6.00
        )
        self.book2 = Book.objects.create(
            title="Test Title",
            author="Test Author",
            inventory=0,
            daily_fee=6.00
        )
        self.borrowing1 = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user2,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_that_the_user_sees_only_their_own_borrowings(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_borrowings_staff_user_sees_all(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_borrowing_decreases_book_inventory(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("borrowings:borrowing-list")
        data = {
            "book": self.book.id,
            "borrow_date": timezone.now().date(),
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_cannot_create_borrowing_if_book_inventory_less_1(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("borrowings:borrowing-list")
        data = {
            "book": self.book2.id,
            "borrow_date": timezone.now().date(),
            "expected_return_date": timezone.now().date() + timedelta(days=7),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No books left in inventory", str(response.data))

    def test_return_borrowing_updates_actual_return_date_and__inventory(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "borrowings:borrowing-return-borrow",
            kwargs={"pk": self.borrowing1.id}
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.book2.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_cannot_return_borrowing_twice(self):
        self.borrowing1.actual_return_date = timezone.now().date()
        self.borrowing1.save()

        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "borrowings:borrowing-return-borrow",
            kwargs={"pk": self.borrowing1.id}
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This borrowing has already been returned.",
            str(response.data)
        )
