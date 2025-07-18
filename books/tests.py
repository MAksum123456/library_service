from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()


class BookViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="simpleuser@gmail.com",
            password="testpassword123",
        )
        self.staff_user = User.objects.create_user(
            email="staffuser@gmail.com",
            password="staffpassword123",
            is_staff=True,
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=3,
            daily_fee=5.00
        )

    def test_list_books_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_books_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-list")
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "inventory": 3,
            "daily_fee": 5.00,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_staff_user(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("books:book-list")
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "inventory": 3,
            "daily_fee": 5.00,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.first().cover, "Hard")

    def test_update_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        data = {
            "title": "Change title",
            "author": "Change author",
            "inventory": 3,
            "daily_fee": 6.00,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_staff_user(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        data = {
            "title": "Change title",
            "author": "Change author",
            "inventory": 3,
            "daily_fee": 6.00,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        data = {
            "title": "Change title",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_book_as_staff_user(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        data = {
            "title": "Change title",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_as_staff_user(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
