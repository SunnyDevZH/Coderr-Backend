from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
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