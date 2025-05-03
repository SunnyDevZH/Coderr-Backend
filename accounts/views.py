from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .models import User, Review
from offers.models import Offer
from django.db.models import Avg
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer, ReviewSerializer, ProfileListSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate


class RegisterView(APIView):
    """
    API-Endpunkt für die Benutzerregistrierung.
    - Erstellt einen neuen Benutzer basierend auf den übermittelten Daten.
    - Gibt ein Authentifizierungstoken und Benutzerdetails zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /register/ - Registriert einen neuen Benutzer.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Benutzer wird über den Serializer erstellt
            token, created = Token.objects.get_or_create(user=user)  # Token für den Benutzer erstellen
            return Response({
                'token': token.key,  # Token zurückgeben
                'username': user.username,
                'email': user.email,
                'user_id': user.id,  # Benutzer-ID zurückgeben
                'type': user.type  # Benutzer-Typ zurückgeben (falls vorhanden)
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API-Endpunkt für die Benutzeranmeldung.
    - Authentifiziert den Benutzer basierend auf den übermittelten Anmeldedaten.
    - Gibt ein Authentifizierungstoken und Benutzerdetails zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /login/ - Meldet einen Benutzer an.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,  # Email hinzufügen
                "user_id": user.id,
                "type": user.type  # Benutzer-Typ hinzufügen
            }, status=status.HTTP_200_OK)
        
        return Response({
            "detail": ["Falsche Anmeldedaten."]
        }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet für die Verwaltung von Benutzerprofilen.
    - Unterstützt CRUD-Operationen für Benutzer.
    - Enthält zusätzliche Endpunkte für Geschäftsnutzer und Kunden.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer  # Standard-Serializer für Detailansichten

    def retrieve(self, request, *args, **kwargs):
        """
        GET /profile/<int:pk>/ - Ruft die Profildetails eines Benutzers ab.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.id != instance.id and not request.user.is_staff:
            return Response({
                "detail": ["Du hast keine Berechtigung, dieses Profil zu bearbeiten."]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='business', permission_classes=[IsAuthenticated])
    def list_business(self, request):
        """
        GET /profiles/business/ - Gibt eine Liste aller Geschäftsnutzer zurück.
        """
        business_users = self.queryset.filter(type='business')
        serializer = ProfileListSerializer(business_users, many=True)  # Verwenden des ProfileListSerializer
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer', permission_classes=[IsAuthenticated])
    def list_customer(self, request):
        """
        GET /profiles/customer/ - Gibt eine Liste aller Kundenprofile zurück.
        """
        customer_users = self.queryset.filter(type='customer')
        serializer = ProfileListSerializer(customer_users, many=True)  # Verwenden des ProfileListSerializer
        return Response(serializer.data)


class BaseInfoView(APIView):
    """
    API-Endpunkt für allgemeine Statistiken und Informationen.
    - Gibt Statistiken zu Bewertungen, Geschäftsnutzern und Angeboten zurück.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        GET /base-info/ - Ruft allgemeine Statistiken ab.
        """
        # Benutzerdefiniertes User-Modell abrufen
        User = get_user_model()

        # Anzahl der Bewertungen
        review_count = Review.objects.count()

        # Durchschnittliches Bewertungsergebnis
        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        average_rating = round(average_rating, 1)

        # Anzahl der Geschäftsnutzer (Business Profile)
        business_profile_count = User.objects.filter(type='business').count()

        # Anzahl der Angebote
        offer_count = Offer.objects.count()

        # Antwort zurückgeben
        return Response({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        })


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        """
        Setzt den aktuellen Benutzer als reviewer.
        """
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """
        Filtert die Bewertungen nach den angegebenen Parametern.
        """
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        ordering = self.request.query_params.get('ordering', '-updated_at')
        
        if business_user_id and business_user_id != 'undefined':
            queryset = queryset.filter(business_user_id=business_user_id)
        
        return queryset.order_by(ordering)

    def list(self, request, *args, **kwargs):
        """
        GET /reviews/ - Ruft eine Liste aller Bewertungen ab.
        """
        queryset = self.get_queryset()
        serialized = self.get_serializer(queryset, many=True)
        return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        """
        POST /reviews/ - Erstellt eine neue Bewertung.
        """
        if request.user.type != 'customer':
            return Response({
                "detail": ["Nur Kunden können Bewertungen erstellen."]
            }, status=status.HTTP_403_FORBIDDEN)

        # Überprüfen, ob der Benutzer bereits eine Bewertung für das Geschäftsprofil abgegeben hat
        business_user_id = request.data.get('business_user')
        if Review.objects.filter(business_user_id=business_user_id, reviewer=request.user).exists():
            return Response({
                "detail": ["Du hast bereits eine Bewertung für dieses Geschäftsprofil abgegeben."]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Falls keine Fehler, Bewertung erstellen
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
