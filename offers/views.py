from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailFullSerializer, OfferListSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'details__price']
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'min_delivery_time']
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """
        Overrides the default serializer selection based on the action.
        - Returns the `OfferListSerializer` for list() action.
        - Returns the `OfferSerializer` for other actions like create, update, etc.
        """
        if self.action == 'list':
            return OfferListSerializer
        return OfferSerializer

    def get_permissions(self):
        """
        Overrides the default permission check.
        - Disables permissions for 'list' and 'retrieve' actions, allowing public access.
        - Requires authentication for other actions (create, update, delete).
        """
        if self.action in ['list', 'retrieve']:  # Allow public access for listing and retrieving
            return []  
        return super().get_permissions()  # For other actions, use default permissions

    def perform_create(self, serializer):
        """
        Overrides the default create behavior to ensure only business users can create offers.
        - Checks if the user is of type 'business' before allowing offer creation.
        """
        user = self.request.user
        if getattr(user, 'type', None) != 'business':
            raise PermissionDenied("Only users with type 'business' can create offers.")
        serializer.save(user=user)

    def get_queryset(self):
        """
        Customizes the queryset for filtering offers based on query parameters.
        - Filters offers based on creator, minimum price, and maximum delivery time.
        """
        queryset = super().get_queryset()
        params = self.request.query_params

        creator_id = params.get('creator_id')
        min_price = params.get('min_price')
        max_delivery_time = params.get('max_delivery_time')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        if min_price:
            try:
                queryset = queryset.filter(min_price__gte=float(min_price))
            except ValueError:
                pass

        if max_delivery_time:
            try:
                queryset = queryset.filter(min_delivery_time__lte=int(max_delivery_time))
            except ValueError:
                pass

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Overrides the default create method to validate and create a new offer.
        - Handles request data validation and returns appropriate error messages if invalid.
        """
        print("Request Data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Overrides the default partial update behavior.
        - Ensures that only the offer creator can update the offer.
        """
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "Only the creator can edit this offer."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Overrides the default destroy method.
        - Ensures that only the offer creator can delete the offer.
        - Deletes associated offer details before deleting the offer itself.
        """
        instance = self.get_object()
        if instance.user != request.user:  # Ensures that only the creator can delete
            return Response(
                {"detail": "Only the creator can delete this offer."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.details.all().delete()  # Delete all offer details
        instance.delete()  # Delete the offer itself
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailFullSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = []  # No authentication required for OfferDetail view

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific offer detail by ID.
        - This method is intended for reading offer details.
        """
        print("Offer ID:", kwargs.get('pk'))
        return super().retrieve(request, *args, **kwargs)
