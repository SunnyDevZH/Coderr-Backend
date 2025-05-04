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
    API endpoint for user registration.
    - Creates a new user based on the provided data.
    - Returns an authentication token and user details.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /register/ - Registers a new user.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  
            token, created = Token.objects.get_or_create(user=user)  
            return Response({
                'token': token.key,  
                'username': user.username,
                'email': user.email,
                'user_id': user.id,  
                'type': user.type  
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.
    - Authenticates the user based on the provided credentials.
    - Returns an authentication token and user details.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /login/ - Logs in a user.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,  
                "user_id": user.id,
                "type": user.type  
            }, status=status.HTTP_200_OK)
        
        return Response({
            "detail": ["Invalid login credentials."]
        }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    - Supports CRUD operations for users.
    - Includes additional endpoints for business users and customers.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer  

    def retrieve(self, request, *args, **kwargs):
        """
        GET /profile/<int:pk>/ - Retrieves the profile details of a user.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /profile/<int:pk>/ - Partially updates a user's profile.
        - Ensures only the user or staff can update the profile.
        """
        instance = self.get_object()

        if request.user.id != instance.id and not request.user.is_staff:
            return Response({
                "detail": ["You do not have permission to edit this profile."]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='business', permission_classes=[IsAuthenticated])
    def list_business(self, request):
        """
        GET /profiles/business/ - Returns a list of all business users.
        """
        business_users = self.queryset.filter(type='business')
        serializer = ProfileListSerializer(business_users, many=True)  
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer', permission_classes=[IsAuthenticated])
    def list_customer(self, request):
        """
        GET /profiles/customer/ - Returns a list of all customer profiles.
        """
        customer_users = self.queryset.filter(type='customer')
        serializer = ProfileListSerializer(customer_users, many=True)  
        return Response(serializer.data)


class BaseInfoView(APIView):
    """
    API endpoint for general statistics and information.
    - Returns statistics about reviews, business users, and offers.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        GET /base-info/ - Retrieves general statistics.
        """
        
        User = get_user_model()

        
        review_count = Review.objects.count()

       
        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        average_rating = round(average_rating, 1)

        
        business_profile_count = User.objects.filter(type='business').count()

        
        offer_count = Offer.objects.count()

        
        return Response({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        })


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    - Supports CRUD operations for reviews.
    - Includes filtering and ordering options.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        """
        Sets the current user as the reviewer.
        """
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """
        Filters reviews based on the provided parameters.
        """
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        ordering = self.request.query_params.get('ordering', '-updated_at')
        
        if business_user_id and business_user_id != 'undefined':
            queryset = queryset.filter(business_user_id=business_user_id)
        
        return queryset.order_by(ordering)

    def list(self, request, *args, **kwargs):
        """
        GET /reviews/ - Retrieves a list of all reviews.
        """
        queryset = self.get_queryset()
        serialized = self.get_serializer(queryset, many=True)
        return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        """
        POST /reviews/ - Creates a new review.
        - Ensures only customers can create reviews.
        - Prevents duplicate reviews for the same business profile.
        """
        if request.user.type != 'customer':
            return Response({
                "detail": ["Only customers can create reviews."]
            }, status=status.HTTP_403_FORBIDDEN)

        business_user_id = request.data.get('business_user')
        if Review.objects.filter(business_user_id=business_user_id, reviewer=request.user).exists():
            return Response({
                "detail": ["You have already reviewed this business profile."]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /reviews/<id>/ - Updates a review.
        - Ensures only the creator of the review can update it.
        """
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({
                "detail": ["Only the creator of this review can edit it."]
            }, status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /reviews/<id>/ - Deletes a review.
        - Ensures only the creator of the review can delete it.
        """
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({
                "detail": ["Only the creator of this review can delete it."]
            }, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

