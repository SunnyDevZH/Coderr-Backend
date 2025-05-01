from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail
from accounts.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer für die Verwaltung von Bestellungen (Orders).
    - Stellt sicher, dass alle Felder standardmäßig schreibgeschützt sind.
    - Unterstützt die Erstellung von Bestellungen basierend auf einem OfferDetail.
    """

    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields  # Alle Felder sind standardmäßig schreibgeschützt

    def create(self, validated_data):
        """
        Erstellt eine neue Bestellung basierend auf einem OfferDetail.
        - `offer_detail`: Das Angebot, auf dem die Bestellung basiert.
        - `customer_user`: Der Benutzer, der die Bestellung erstellt (aus dem Kontext).
        - `business_user`: Der Benutzer, der das Angebot erstellt hat.

        Validierte Daten werden mit den Informationen aus dem OfferDetail ergänzt.
        """
        offer_detail = validated_data.get('offer_detail')
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

        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Überschreibt die Standard-Darstellung einer Bestellung.
        - Fügt Standardwerte für `features` und `status` hinzu, falls diese fehlen.
        """
        representation = super().to_representation(instance)
        # Sicherstellen, dass gewisse Felder Defaults liefern, falls sie fehlen
        representation['features'] = representation.get('features') or []
        representation['status'] = representation.get('status') or 'unknown'
        return representation
