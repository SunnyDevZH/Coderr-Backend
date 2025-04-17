# filepath: accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LoginView, UserViewSet, BaseInfoView, ReviewViewSet

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]