from django.contrib.auth import get_user_model  # Verwende get_user_model statt User direkt zu importieren
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Offer, OfferDetail

# Hole das benutzerdefinierte User-Modell
User = get_user_model()

# Kurze Version für OfferDetail für List-View (id + url)
class OfferDetailShortSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')


# Volle Version für OfferDetail für Detail-View (ohne url!)
class OfferDetailFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def validate(self, data):
        if data['offer_type'] not in ['basic', 'standard', 'premium']:
            raise ValidationError("Invalid offer type. Must be 'basic', 'standard', or 'premium'.")
        if data['delivery_time_in_days'] <= 0:
            raise ValidationError("Delivery time must be a positive integer.")
        if data['revisions'] < -1:
            raise ValidationError("Revisions must be -1 or greater.")
        if not data.get('features'):
            raise ValidationError("At least one feature must be provided.")
        return data


# Serializer für Offer List
class OfferListSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    details = OfferDetailShortSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }


# Serializer für Offer Detail
class OfferSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, write_only=True)  # Hier machen wir user als nicht erforderlich
    user_details = serializers.SerializerMethodField()
    details = OfferDetailFullSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }
