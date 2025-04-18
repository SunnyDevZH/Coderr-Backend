from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_user', 'business_user', 'status']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']

    def get_permissions(self):
        """
        Setzt die Berechtigungen basierend auf der Anfrage.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Authentifizierung erforderlich
        return [AllowAny()]  # GET-Endpunkte sind öffentlich zugänglich

    def get_queryset(self):
        """
        Filtert Bestellungen basierend auf den Query-Parametern.
        """
        queryset = super().get_queryset()
        customer_user_id = self.request.query_params.get('customer_user_id')
        business_user_id = self.request.query_params.get('business_user_id')
        status = self.request.query_params.get('status')
        ordering = self.request.query_params.get('ordering', '-created_at')

        if customer_user_id:
            queryset = queryset.filter(customer_user_id=customer_user_id)
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if status:
            queryset = queryset.filter(status=status)
        queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Erstellt eine neue Bestellung.
        """
        data = request.data
        data['customer_user'] = request.user.id  # Setzt den authentifizierten Benutzer als Kunden
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Aktualisiert eine Bestellung teilweise.
        """
        instance = self.get_object()
        if instance.customer_user != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to edit this order."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Löscht eine Bestellung. Nur Admins können Bestellungen löschen.
        """
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

    def list(self, request, *args, **kwargs):
        """
        Überschreibt die Standard-List-Methode, um sicherzustellen, dass die Antwort immer ein Array ist.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CustomerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer_user=request.user)
        if not orders.exists():
            # Rückgabe einer Standardantwort, wenn keine Bestellungen vorhanden sind
            return Response({"orders": [], "message": "Keine Bestellungen gefunden."})
        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})

class OrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        """
        Gibt die Anzahl der laufenden Bestellungen (Status: in_progress) eines Geschäftsnutzers zurück.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        order_count = Order.objects.filter(user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})


class CompletedOrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        """
        Gibt die Anzahl der abgeschlossenen Bestellungen (Status: completed) eines Geschäftsnutzers zurück.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        completed_order_count = Order.objects.filter(user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})
