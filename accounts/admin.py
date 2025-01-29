from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'username', 'type', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'type', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password', 'username', 'type')}),
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
    readonly_fields = ('id',)  # Entferne 'token', wenn es nicht existiert

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)
