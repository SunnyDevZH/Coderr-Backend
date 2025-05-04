from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Offer, OfferDetail

User = get_user_model()


class OfferDetailShortSerializer(serializers.ModelSerializer):
    """
    Serializer for a short representation of OfferDetail.
    - Includes only the ID and a generated URL for the detail.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Generates a URL for the OfferDetail object.
        """
        return f"/offerdetails/{obj.id}/"


class OfferDetailFullSerializer(serializers.ModelSerializer):
    """
    Serializer for a full representation of OfferDetail.
    - Includes all fields of the OfferDetail model.
    """

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def validate(self, data):
        """
        Validates the OfferDetail data.
        - Ensures the offer type is valid.
        - Ensures delivery time is positive.
        - Ensures revisions are -1 or greater.
        - Ensures at least one feature is provided.
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
    Serializer for listing offers.
    - Includes user details and a short representation of associated OfferDetails.
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
        Retrieves user details for the offer creator.
        - Includes first name, last name, and username.
        """
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating, and retrieving offers.
    - Includes full details of associated OfferDetails.
    """

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
        """
        Retrieves user details for the offer creator.
        - Includes first name, last name, and username.
        """
        user = obj.user
        return {
            "first_name": user.first_name or "Unbekannt",
            "last_name": user.last_name or "Unbekannt",
            "username": user.username
        }

    def validate_details(self, value):
        """
        Validates the details of the offer.
        - Ensures exactly 3 details are provided (basic, standard, premium).
        - Ensures each detail has a unique and valid offer type.
        """
        if len(value) != 3:
            raise ValidationError("Exactly 3 offer details are required (basic, standard, premium).")
        offer_types = {detail['offer_type'] for detail in value}
        required_types = {'basic', 'standard', 'premium'}
        if offer_types != required_types:
            raise ValidationError(f"Offer must contain exactly one of each type: {', '.join(required_types)}.")
        return value

    def create(self, validated_data):
        """
        Creates a new offer with associated details.
        - Calculates and sets the minimum price and delivery time.
        """
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
        """
        Updates an existing offer and its associated details.
        - Ensures details are updated or created as needed.
        - Recalculates the minimum price and delivery time.
        """
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                if not offer_type:
                    raise ValidationError("Each detail must include an 'offer_type' field.")

                try:
                    detail = instance.details.get(offer_type=offer_type)
                    for key, val in detail_data.items():
                        setattr(detail, key, val)
                    detail.save()
                except OfferDetail.DoesNotExist:
                    OfferDetail.objects.create(offer=instance, **detail_data)

           
            prices = [d.price for d in instance.details.all()]
            times = [d.delivery_time_in_days for d in instance.details.all()]
            instance.min_price = min(prices)
            instance.min_delivery_time = min(times)
            instance.save()

        return instance

