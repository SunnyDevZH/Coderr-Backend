from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .serializers import RegistrationSerializer, LoginSerializer, CustomUserSerializer
from .models import CustomUser

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
                'type': user.type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
                'type': user.type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_type = self.request.query_params.get('type')
        if user_type:
            queryset = queryset.filter(type=user_type)
        return queryset

    @action(detail=False, methods=['get'], url_path='business')
    def list_business(self, request):
        queryset = self.get_queryset().filter(type='business')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer')
    def list_customer(self, request):
        queryset = self.get_queryset().filter(type='customer')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')  # Extrahiere den pk-Parameter aus den URL-Argumenten
        if pk is None:
            return Response({"detail": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = self.get_queryset().get(pk=pk)  # Finde den Benutzer mit dem entsprechenden pk
        except CustomUser.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)  # Serialisiere die Benutzerdaten
        return Response(serializer.data)
