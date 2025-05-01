from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'', OfferViewSet, basename='offers') 

urlpatterns = [
    path('', include(router.urls)),
]
