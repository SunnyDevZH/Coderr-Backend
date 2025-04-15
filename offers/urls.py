from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'', OfferViewSet, basename='offers')  # Endpunkt: /api/offers/

urlpatterns = [
    path('', include(router.urls)),  # Bezieht sich auf /api/offers/
   
]