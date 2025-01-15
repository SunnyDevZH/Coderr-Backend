# filepath: accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, registration_view, CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration-page/', registration_view, name='registration_page'),
    # Füge spezifische Endpunkte hinzu, falls benötigt
    path('base-info/', CustomUserViewSet.as_view({'get': 'list'}), name='base-info'),
    path('profile/<int:pk>/', CustomUserViewSet.as_view({'get': 'retrieve'}), name='profile'),
]