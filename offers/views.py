from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import NotFound


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]  # TokenAuthentication verwenden
    permission_classes = [IsAuthenticated]  # Nur authentifizierte Benutzer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['details__price', 'details__delivery_time_in_days']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'details__price']

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering', '-updated_at')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            try:
                queryset = queryset.filter(details__price__gte=float(min_price))
            except ValueError:
                pass
        if max_delivery_time:
            try:
                queryset = queryset.filter(details__delivery_time_in_days__lte=int(max_delivery_time))
            except ValueError:
                pass
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)
        if ordering:
            queryset = queryset.order_by(ordering)

        print("Queryset:", queryset)  # Debugging hinzufügen
        return queryset

    def create(self, request, *args, **kwargs):
        print("Request Data:", request.data)  # Debugging hinzufügen
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # Debugging hinzufügen
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.details.all().delete()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Gibt eine Liste aller Angebote zurück. Wenn keine Angebote vorhanden sind, wird ein leeres Array zurückgegeben.
        """
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response([], status=status.HTTP_200_OK)  # Leeres Array zurückgeben
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    authentication_classes = [TokenAuthentication]  # TokenAuthentication verwenden
    permission_classes = [IsAuthenticated]  # Nur authentifizierte Benutzer

    def retrieve(self, request, *args, **kwargs):
        print("Offer ID:", kwargs.get('pk'))  # Debugging hinzufügen
        return super().retrieve(request, *args, **kwargs)
