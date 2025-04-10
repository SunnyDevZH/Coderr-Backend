from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet)  # Endpunkt: /api/offers/
router.register(r'offerdetails', OfferDetailViewSet)  # Endpunkt: /api/offerdetails/

urlpatterns = [
    path('', include(router.urls)),
]