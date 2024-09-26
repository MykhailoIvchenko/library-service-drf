from rest_framework import mixins, viewsets

from borrowings.models import Borrowing
from borrowings.permissions import IsOwnerOrAdmin
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailsSerializer, \
    CreateBorrowingSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book")
    permission_classes = [IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailsSerializer

        if self.action == "create":
            return CreateBorrowingSerializer

        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id is not None:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            is_active = is_active.lower() in ["true", "yes"]
            queryset = queryset.filter(actual_return_date__isnull=True) if is_active else queryset.filter(
                actual_return_date__isnull=False)

        return queryset
