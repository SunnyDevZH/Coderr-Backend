from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'customer_user', 'business_user', 'status', 'created_at', 'updated_at')
    search_fields = ('title', 'customer_user__username', 'business_user__username')
    list_filter = ('status', 'created_at')
