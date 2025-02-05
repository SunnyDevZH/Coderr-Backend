from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['customer_user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            instance.status = request.data['status']
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"detail": "Only status can be updated."}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_staff:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Only admin users can delete orders."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], url_path='order-count/(?P<business_user_id>[^/.]+)', permission_classes=[AllowAny])
    def order_count(self, request, business_user_id=None):
        business_user = get_object_or_404(User, pk=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})

    @action(detail=False, methods=['get'], url_path='completed-order-count/(?P<business_user_id>[^/.]+)', permission_classes=[AllowAny])
    def completed_order_count(self, request, business_user_id=None):
        business_user = get_object_or_404(User, pk=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})
