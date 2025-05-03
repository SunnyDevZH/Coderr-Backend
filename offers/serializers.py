from django.contrib.auth import get_user_model  # Verwende get_user_model statt User direkt zu importieren
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Offer, OfferDetail

# Hole das benutzerdefinierte User-Modell
User = get_user_model()


class OfferDetailShortSerializer(serializers.ModelSerializer):
    """
    Serializer für die Kurzversion von Angebotsdetails (OfferDetail).
    - Wird in der Angebotsliste verwendet, um nur die ID und die URL der Details darzustellen.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Gibt nur den relativen Pfad zur Detailansicht zurück (z. B. /offerdetails/1/),
        wie in der API-Dokumentation gefordert.
        """
        return f"/offerdetails/{obj.id}/"


class OfferDetailFullSerializer(serializers.ModelSerializer):
    """
    Serializer für die vollständige Darstellung von Angebotsdetails (OfferDetail).
    - Wird verwendet, um alle relevanten Felder eines Angebotsdetails darzustellen.
    """

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def validate(self, data):
        """
        Validiert die Eingabedaten für ein Angebotsdetail.
        - `offer_type`: Muss einer der Werte 'basic', 'standard' oder 'premium' sein.
        - `delivery_time_in_days`: Muss eine positive Zahl sein.
        - `revisions`: Muss -1 oder größer sein.
        - `features`: Mindestens ein Feature muss angegeben werden.
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


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Liste von Angeboten (Offer).
    - Wird verwendet, um eine kompakte Darstellung von Angeboten zu liefern.
    - Enthält grundlegende Felder und eine Kurzversion der Angebotsdetails.
    """

    user_details = serializers.SerializerMethodField()
    details = OfferDetailShortSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        """
        Gibt die Benutzerdetails des Angebotsbesitzers zurück.
        - Enthält den Vornamen, Nachnamen und Benutzernamen.
        """
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    user_details = serializers.SerializerMethodField()
    details = OfferDetailFullSerializer(many=True)

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

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)

        min_price = None
        min_delivery_time = None

        for detail_data in details_data:
            detail = OfferDetail.objects.create(offer=offer, **detail_data)
        
            if min_price is None or detail.price < min_price:
                min_price = detail.price
            if min_delivery_time is None or detail.delivery_time_in_days < min_delivery_time:
                min_delivery_time = detail.delivery_time_in_days

        offer.min_price = min_price
        offer.min_delivery_time = min_delivery_time
        offer.save()

        return offer
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        # Update die Felder des Offers
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Wenn neue details übergeben wurden, ersetze die alten komplett
        if details_data is not None:
            # Bestehende OfferDetails löschen
            instance.details.all().delete()

            min_price = None
            min_delivery_time = None

            for detail_data in details_data:
                detail = OfferDetail.objects.create(offer=instance, **detail_data)

                if min_price is None or detail.price < min_price:
                    min_price = detail.price
                if min_delivery_time is None or detail.delivery_time_in_days < min_delivery_time:
                    min_delivery_time = detail.delivery_time_in_days

            instance.min_price = min_price
            instance.min_delivery_time = min_delivery_time
            instance.save()

        return instance
