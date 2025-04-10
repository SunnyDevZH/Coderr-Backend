from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            instance.status = request.data['status']
            instance.save()
            return Response(self.get_serializer(instance).data)
        return Response({"detail": "Only the status field can be updated."}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='order-count/(?P<business_user_id>[^/.]+)', permission_classes=[AllowAny])
    def order_count(self, request, business_user_id=None):
        """
        Gibt die Anzahl der laufenden Bestellungen (Status: in_progress) eines Geschäftsnutzers zurück.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})

    @action(detail=False, methods=['get'], url_path='completed-order-count/(?P<business_user_id>[^/.]+)', permission_classes=[AllowAny])
    def completed_order_count(self, request, business_user_id=None):
        """
        Gibt die Anzahl der abgeschlossenen Bestellungen (Status: completed) eines Geschäftsnutzers zurück.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})
