from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailFullSerializer, OfferListSerializer

class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet für die Verwaltung von Angeboten (Offers).
    Unterstützt CRUD-Operationen sowie Filter-, Such- und Sortierfunktionen.
    """

    queryset = Offer.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'details__price']  # Unterstützt Filterung nach Benutzer und Preis
    search_fields = ['title', 'description']  # Unterstützt Suche nach Titel und Beschreibung
    ordering_fields = ['min_price', 'min_delivery_time']  # Unterstützt Sortierung nach Preis und Lieferzeit
    pagination_class = PageNumberPagination  # Aktiviert die Paginierung

    def get_serializer_class(self):
        """
        Gibt den Serializer zurück, der für die aktuelle Aktion verwendet werden soll.
        - Für die `list`-Aktion wird der `OfferListSerializer` verwendet.
        - Für alle anderen Aktionen wird der `OfferSerializer` verwendet.
        """
        if self.action == 'list':
            return OfferListSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        """
        Überschreibt die Standard-Logik für das Erstellen eines neuen Angebots.
        - Setzt den authentifizierten Benutzer (`self.request.user`) als Eigentümer des Angebots.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Gibt das Queryset zurück, das für die aktuelle Anfrage verwendet wird.
        Unterstützt folgende Filter:
        - `creator_id`: Filtert Angebote nach der ID des Erstellers.
        - `min_price`: Filtert Angebote mit einem Mindestpreis.
        - `search`: Sucht nach Angeboten basierend auf dem Titel oder der Beschreibung.
        """
        queryset = super().get_queryset()
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        search = self.request.query_params.get('search')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Erstellt ein neues Angebot.
        - Validiert die Anfrage-Daten.
        - Setzt den authentifizierten Benutzer als Eigentümer des Angebots.
        """
        print("Request Data:", request.data)  # Debugging: Gibt die Request-Daten aus
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # Fehler beim Validieren
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Aktualisiert bestimmte Felder eines bestehenden Angebots.
        - Unterstützt nur die Felder, die in der Anfrage angegeben sind.
        """
        print("Partial Update Request Data:", request.data)  # Debugging: Gibt die Request-Daten aus
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Aktualisiert ein bestehendes Angebot vollständig.
        - Ersetzt alle Felder des Angebots mit den in der Anfrage angegebenen Werten.
        """
        print("Update Request Data:", request.data)  # Debugging: Gibt die Request-Daten aus
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Löscht ein bestehendes Angebot.
        - Löscht auch alle zugehörigen Angebotsdetails.
        """
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
        print("Offer ID:", kwargs.get('pk'))  # Debugging: Gibt die Offer-ID aus
        return super().retrieve(request, *args, **kwargs)
