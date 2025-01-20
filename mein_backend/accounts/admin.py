from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'type', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'type', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'type', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username',)
    ordering = ('email',)
    readonly_fields = ('id',)  # Make the id field read-only

admin.site.register(CustomUser, CustomUserAdmin)
