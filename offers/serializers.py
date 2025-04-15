from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Offer, OfferDetail
from accounts.serializers import UserSerializer


class OfferDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # <--- DAS ist wichtig
    
    class Meta:
        model = OfferDetail
        fields = '__all__'

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = '__all__'

    def validate_details(self, value):
        if len(value) != 3:
            raise ValidationError("An offer must have exactly 3 details (basic, standard, premium).")
        
        offer_types = [detail.get('offer_type') for detail in value]
        if set(offer_types) != {'basic', 'standard', 'premium'}:
            raise ValidationError("Each offer must include one 'basic', one 'standard', and one 'premium' detail.")
        
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer