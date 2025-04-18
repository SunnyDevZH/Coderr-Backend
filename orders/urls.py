from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderCountView, CompletedOrderCountView

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')  # Endpunkt: /api/orders/

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
]