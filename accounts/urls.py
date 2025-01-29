# filepath: accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LoginView, CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('base-info/', CustomUserViewSet.as_view({'get': 'list'}), name='base-info'),
    path('profile/<int:pk>/', CustomUserViewSet.as_view({'get': 'retrieve'}), name='profile'),
    path('profiles/business/', CustomUserViewSet.as_view({'get': 'list_business'}), name='profiles-business'),
    path('profiles/customer/', CustomUserViewSet.as_view({'get': 'list_customer'}), name='profiles-customer'),
]