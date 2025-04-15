from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'', OfferViewSet, basename='offers')  # Endpunkt: /api/offers/
router.register(r'details', OfferDetailViewSet, basename='offerdetails')  # Endpunkt: /api/offers/details/

urlpatterns = [
    path('', include(router.urls)),
]