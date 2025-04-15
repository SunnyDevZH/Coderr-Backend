from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission, AllowAny
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Nur der Besitzer oder ein Admin hat Zugriff
        return obj.user == request.user or request.user.is_staff

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'details__price']

    def get_permissions(self):
        """
        Setzt die Berechtigungen basierend auf der Anfrage.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Authentifizierung erforderlich
        return [AllowAny()]  # GET-Endpunkte sind öffentlich zugänglich

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
        Erstellt ein neues Angebot.
        """
        data = request.data
        data['user'] = request.user.id  # Setzt den Benutzer als Eigentümer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Aktualisiert ein Angebot teilweise.
        """
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to edit this offer."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Löscht ein Angebot und die zugehörigen Angebotsdetails.
        """
        instance = self.get_object()
        if request.user != instance.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to delete this offer."}, status=status.HTTP_403_FORBIDDEN)
        instance.details.all().delete()  # Löscht die zugehörigen Angebotsdetails
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]
