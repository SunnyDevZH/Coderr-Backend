from django.contrib import admin
from .models import Offer, OfferDetail
from django.db import models

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'min_price', 'min_delivery_time', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')

    def min_price(self, obj):
        # Beispiel: Berechnung des minimalen Preises aus OfferDetails
        return obj.details.aggregate(models.Min('price'))['price__min']

    def min_delivery_time(self, obj):
        # Beispiel: Berechnung der minimalen Lieferzeit aus OfferDetails
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min']

    min_price.short_description = 'Min Price'
    min_delivery_time.short_description = 'Min Delivery Time'

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'offer_type', 'price', 'delivery_time_in_days')
    search_fields = ('title',)
    list_filter = ('offer_type',)
