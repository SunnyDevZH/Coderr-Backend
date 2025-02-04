from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet)
router.register(r'offerdetails', OfferDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]