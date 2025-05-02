from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group  # Importiere das Group-Modell
from .models import User, Review  # Importiere das Review-Modell

# Deregistriere das Group-Modell, um es aus dem Admin zu entfernen
admin.site.unregister(Group)

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

class ReviewAdmin(admin.ModelAdmin):
    """
    Admin-Klasse für das Review-Modell.
    - Zeigt die gewünschten Felder in der Admin-Oberfläche an.
    """
    model = Review
    list_display = ('id', 'get_business_user', 'get_reviewer', 'rating', 'get_description', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'updated_at')
    search_fields = ('business_user__username', 'reviewer__username', 'description')
    readonly_fields = ('created_at', 'updated_at')

    def get_business_user(self, obj):
        """
        Gibt den Benutzernamen des Geschäftsnutzers zurück.
        """
        return obj.business_user.username if obj.business_user else "Unbekannt"
    get_business_user.short_description = "Business User"

    def get_reviewer(self, obj):
        """
        Gibt den Benutzernamen des Bewertenden zurück.
        """
        return obj.reviewer.username if obj.reviewer else "Unbekannt"
    get_reviewer.short_description = "Reviewer"

    def get_description(self, obj):
        """
        Gibt die Beschreibung der Bewertung zurück.
        """
        return obj.description or "Keine Beschreibung"
    get_description.short_description = "Description"

# Registriere die Modelle im Admin
admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
