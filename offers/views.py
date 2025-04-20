from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['details__price', 'details__delivery_time_in_days']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'details__price']

    def get_permissions(self):
        """
        Nur authentifizierte Benutzer haben Zugriff auf diese Endpunkte.
        """
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filtert Angebote basierend auf den Query-Parametern.
        """
        queryset = super().get_queryset()
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering', '-updated_at')

        # Filter nur anwenden, wenn die Query-Parameter nicht leer sind
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            try:
                queryset = queryset.filter(details__price__gte=float(min_price))
            except ValueError:
                pass  # Ignoriere ungültige Werte
        if max_delivery_time:
            try:
                queryset = queryset.filter(details__delivery_time_in_days__lte=int(max_delivery_time))
            except ValueError:
                pass  # Ignoriere ungültige Werte
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Erstellt ein neues Angebot mit dem authentifizierten Benutzer.
        """

        print("👤 request.user:", request.user)
        print("🔐 request.auth:", request.auth)

        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                        status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)  # Debugging-Ausgabe
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def partial_update(self, request, *args, **kwargs):
        """
        Aktualisiert ein Angebot teilweise.
        """
        instance = self.get_object()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Löscht ein Angebot und die zugehörigen Angebotsdetails.
        """
        instance = self.get_object()
        instance.details.all().delete()  # Löscht die zugehörigen Angebotsdetails
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]  # Alle Endpunkte sind öffentlich zugänglich
