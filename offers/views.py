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
        if self.action == 'list':
            return OfferListSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'profile') or getattr(user.profile, 'type', None) != 'business':
            raise PermissionDenied("Only users with type 'business' can create offers.")
        serializer.save(user=user)

    def get_queryset(self):
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
        print("Request Data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "Nur der Ersteller darf dieses Angebot bearbeiten."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.details.all().delete()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailFullSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        print("Offer ID:", kwargs.get('pk'))
        return super().retrieve(request, *args, **kwargs)
