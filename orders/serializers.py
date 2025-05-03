from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer für die Verwaltung von Bestellungen (Orders).
    - Unterstützt die Erstellung von Bestellungen basierend auf einem OfferDetail.
    - Stellt sicher, dass alle Felder standardmäßig schreibgeschützt sind.
    """

    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())  # Der Benutzer gibt nur die ID des OfferDetails an
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)  # Wird automatisch gesetzt basierend auf dem authentifizierten Benutzer
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)  # Wird automatisch gesetzt basierend auf dem OfferDetail

    # Markiere die Felder, die aus dem OfferDetail übernommen werden, als read_only
    title = serializers.CharField(read_only=True)
    revisions = serializers.IntegerField(read_only=True)
    delivery_time_in_days = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    features = serializers.ListField(read_only=True)
    offer_type = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'offer_detail_id', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Erstellt eine neue Bestellung basierend auf einem OfferDetail.
        """
        offer_detail = validated_data.pop('offer_detail_id')  # Hole das OfferDetail-Objekt
        print("OfferDetail:", offer_detail)  # Debugging

        # Hole den authentifizierten Benutzer und den Anbieter des Angebots
        customer_user = self.context['request'].user
        business_user = offer_detail.offer.user

        # Ergänze die validierten Daten mit den Details aus dem OfferDetail
        validated_data.update({
            'customer_user': customer_user,
            'business_user': business_user,
            'title': offer_detail.title,
            'revisions': offer_detail.revisions,
            'delivery_time_in_days': offer_detail.delivery_time_in_days,
            'price': offer_detail.price,
            'features': offer_detail.features,
            'offer_type': offer_detail.offer_type,
        })

        # Setze die ID des OfferDetail in die Daten
        validated_data['offer_detail_id'] = offer_detail.id

        # Erstelle die Bestellung
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Überschreibt die Standard-Darstellung einer Bestellung.
        - Fügt Standardwerte für `features` und `status` hinzu, falls diese fehlen.
        """
        representation = super().to_representation(instance)
        # Sicherstellen, dass gewisse Felder Defaults liefern, falls sie fehlen
        representation['features'] = representation.get('features') or []
        representation['status'] = representation.get('status') or 'in_progress'  # Standardstatus
        return representation
