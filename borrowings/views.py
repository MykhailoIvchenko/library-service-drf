from rest_framework import mixins, viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailsSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailsSerializer

        return BorrowingSerializer
