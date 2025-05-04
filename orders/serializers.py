from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for managing orders.
    - Supports creating orders based on an existing OfferDetail.
    - Ensures that most fields are read-only by default to preserve offer data integrity.
    """

    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())  # User only provides the ID of the OfferDetail
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)  # Automatically set based on the authenticated user
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)  # Automatically set based on the related OfferDetail's creator

    # Fields copied from the related OfferDetail, marked as read-only
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
        Creates a new order based on the selected OfferDetail.
        - Automatically fills in all related offer attributes into the order.
        """
        offer_detail = validated_data.pop('offer_detail_id')  
        print("OfferDetail:", offer_detail)  

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

        validated_data['offer_detail_id'] = offer_detail.id
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Overrides the default representation of an order.
        - Ensures default values for 'features' and 'status' if missing.
        """
        representation = super().to_representation(instance)
        representation['features'] = representation.get('features') or []
        representation['status'] = representation.get('status') or 'in_progress'  # Default status
        return representation
