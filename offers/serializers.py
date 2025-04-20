from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Offer, OfferDetail
from rest_framework.reverse import reverse


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def validate(self, data):
        """
        Validierung, um sicherzustellen, dass alle erforderlichen Felder vorhanden sind.
        """
        if data['offer_type'] not in ['basic', 'standard', 'premium']:
            raise ValidationError("Invalid offer type. Must be 'basic', 'standard', or 'premium'.")
        
        if data['delivery_time_in_days'] <= 0:
            raise ValidationError("Delivery time must be a positive integer.")
        
        if data['revisions'] < -1:
            raise ValidationError("Revisions must be -1 or greater.")
        
        if not data.get('features'):
            raise ValidationError("At least one feature must be provided.")
        
        return data


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    user_details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]
        # Entferne das `user`-Feld hier, da es nicht im POST-Body erforderlich ist.

    def get_details(self, obj):
        try:
            request = self.context.get('request', None)
            return [
                {
                    "id": detail.id,
                    "url": reverse('offerdetail-detail', args=[detail.id], request=request) if request else None
                }
                for detail in obj.details.all()
            ]
        except Exception as e:
            print("Fehler in get_details:", e)
            return []

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }

    def get_min_price(self, obj):
        return min([d.price for d in obj.details.all()]) if obj.details.exists() else None
    
    def get_min_delivery_time(self, obj):
        return min([d.delivery_time_in_days for d in obj.details.all()]) if obj.details.exists() else None

    def validate(self, data):
        """
        Validierung der Angebotsdaten, um sicherzustellen, dass genau 3 Details vorhanden sind.
        """
        details = data.get('details')
        
        if len(details) != 3:
            raise ValidationError("Exactly three offer details must be provided (basic, standard, premium).")
        
        offer_types = [detail['offer_type'] for detail in details]
        required_types = ['basic', 'standard', 'premium']
        
        if not all(offer_type in offer_types for offer_type in required_types):
            raise ValidationError(f"Offer details must contain {', '.join(required_types)} types.")
        
        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')

        try:
            # Überprüfe, ob der Benutzer authentifiziert ist
            user = self.context['request'].user
            if not user.is_authenticated:
                raise ValidationError("Authentication credentials were not provided.")
        
            # Erstelle das Angebot und weise es dem Benutzer zu
            offer = Offer.objects.create(user=user, **validated_data)
         
            # Erstelle die Angebotdetails
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)
         
            return offer

        except Exception as e:
            # Fehlerprotokollierung
            print(f"Fehler beim Erstellen des Angebots: {e}")
            raise ValidationError(f"Error creating offer: {str(e)}")
