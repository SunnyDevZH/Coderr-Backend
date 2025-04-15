from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail
from accounts.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer_user = UserSerializer(read_only=True)
    business_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']

    def create(self, validated_data):
        offer_detail = validated_data.get('offer_detail')
        customer_user = self.context['request'].user
        business_user = offer_detail.offer.user  # Der Anbieter des Angebots

        # Automatisch die Felder aus OfferDetail übernehmen
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
        # Standardwerte hinzufügen, falls bestimmte Felder fehlen
        representation = super().to_representation(instance)
        representation['features'] = representation.get('features', [])
        representation['status'] = representation.get('status', 'unknown')
        return representation