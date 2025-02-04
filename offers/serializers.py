from rest_framework import serializers
from .models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = '__all__'

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer