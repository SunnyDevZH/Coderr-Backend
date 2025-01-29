from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class UserAdmin(UserAdmin):
    model = User
    list_display = ('user_id', 'email', 'username', 'type', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'type', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('user_id', 'email', 'password', 'username', 'type', 'file', 'location', 'tel', 'description', 'working_hours', 'created_at')}),
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
    readonly_fields = ('user_id', 'created_at')

admin.site.register(User, UserAdmin)
