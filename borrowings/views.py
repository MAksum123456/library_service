from django.utils import timezone

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.serializers import (
    BorrowSerializer,
    BorrowRetrieveSerializer,
    CreateBorrowSerializer,
    BorrowingReturnSerializer,
)
from borrowings.models import Borrowing


@extend_schema_view(
    list=extend_schema(
        tags=["Borrowing"],
        description="List borrowings with optional filters:"
                    " user_id, is_active",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                required=False,
                description="Filter by user_id",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.STR,
                required=False,
                description="Filter by is_active status",
            ),
        ],
    )
)
class BorrowListView(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if self.request.user.is_staff and user_id:
            queryset = queryset.filter(user__id=user_id)

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            if is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowSerializer
        if self.action == "retrieve":
            return BorrowRetrieveSerializer
        if self.action in ("create", "update"):
            return CreateBorrowSerializer
        if self.action == "return_borrow":
            return BorrowingReturnSerializer
        return BorrowSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="return",
    )
    def return_borrow(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {"detail": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            borrowing.actual_return_date = timezone.now()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

        return Response(
            {"status": "Book returned!"},
            status=status.HTTP_200_OK
        )
