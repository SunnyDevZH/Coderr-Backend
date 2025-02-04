from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
   

    def get_queryset(self):
        user = self.request.user
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

    @action(detail=True, methods=['get'], url_path='order-count')
    def order_count(self, request, pk=None):
        business_user = get_object_or_404(User, pk=pk)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})

    @action(detail=True, methods=['get'], url_path='completed-order-count')
    def completed_order_count(self, request, pk=None):
        business_user = get_object_or_404(User, pk=pk)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})
