# filepath: accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LoginView, UserViewSet, BaseInfoView, ReviewViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile'),
    path('profiles/business/', UserViewSet.as_view({'get': 'list_business'}), name='profiles-business'),
    path('profiles/customer/', UserViewSet.as_view({'get': 'list_customer'}), name='profiles-customer'),
]