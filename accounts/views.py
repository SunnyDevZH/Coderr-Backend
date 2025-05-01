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
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Review
from .serializers import ReviewSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
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
        """
        PATCH /profile/<int:pk>/ - Aktualisiert bestimmte Profildetails.
        """
        instance = self.get_object()
        if request.user != instance and not request.user.is_staff:
            return Response({"detail": "You do not have permission to edit this profile."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='business', permission_classes=[AllowAny])
    def list_business(self, request):
        """
        GET /profiles/business/ - Gibt eine Liste aller Geschäftsnutzer zurück.
        """
        business_users = self.queryset.filter(type='business')
        serializer = ProfileListSerializer(business_users, many=True)  # Verwenden des ProfileListSerializer
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer', permission_classes=[AllowAny])
    def list_customer(self, request):
        """
        GET /profiles/customer/ - Gibt eine Liste aller Kundenprofile zurück.
        """
        customer_users = self.queryset.filter(type='customer')
        serializer = ProfileListSerializer(customer_users, many=True)  # Verwenden des ProfileListSerializer
        return Response(serializer.data)

class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
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
    permission_classes = [AllowAny]
    pagination_class = None  

    def get_queryset(self):
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        ordering = self.request.query_params.get('ordering', '-updated_at')

        if business_user_id and business_user_id != 'undefined':
            queryset = queryset.filter(user_id=business_user_id)
        return queryset.order_by(ordering)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized = self.get_serializer(queryset, many=True)
        return Response(serialized.data)  # 🔥 Nur das Array, kein Wrapper

    @action(detail=False, methods=['post'])
    def create_review(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 