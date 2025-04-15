"""
URL configuration for mein_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import RegisterView, LoginView, BaseInfoView, UserViewSet
from offers.views import OfferDetailViewSet  # Import für OfferDetailViewSet
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # Präfix für Accounts
    path('api/orders/', include('orders.urls')),      # Präfix für Orders
    path('api/offers/', include('offers.urls')),      # Präfix für Offers
    path('api/offerdetails/<int:pk>/', OfferDetailViewSet.as_view({'get': 'retrieve'}), name='offerdetails'),  # Endpunkt: /api/offerdetails/<id>/
    path('api/registration/', RegisterView.as_view(), name='registration'),  # Registrierung
    path('api/login/', LoginView.as_view(), name='login'),  # Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token-Refresh
    path('api/base-info/', BaseInfoView.as_view(), name='base-info'),  # Basisinformationen
    path('api/profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile'),  # Benutzerprofil
    path('api/profiles/business/', UserViewSet.as_view({'get': 'list_business'}), name='profiles-business'),  # Geschäftsnutzer
    path('api/profiles/customer/', UserViewSet.as_view({'get': 'list_customer'}), name='profiles-customer'),  # Kundenprofile
    path('api/reviews/', include('accounts.urls')),  # Reviews (falls benötigt)
]
