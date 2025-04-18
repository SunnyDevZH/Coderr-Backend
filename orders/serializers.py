from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail
from accounts.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields  # alles readonly, außer beim POST brauchst du nur offer_detail

    def create(self, validated_data):
        offer_detail = validated_data.get('offer_detail')
        customer_user = self.context['request'].user
        business_user = offer_detail.offer.user

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
        representation = super().to_representation(instance)
        # Optional: Sicherstellen, dass gewisse Felder im Notfall Defaults liefern
        representation['features'] = representation.get('features') or []
        representation['status'] = representation.get('status') or 'unknown'
        return representation
