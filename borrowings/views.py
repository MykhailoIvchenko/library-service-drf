from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

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
