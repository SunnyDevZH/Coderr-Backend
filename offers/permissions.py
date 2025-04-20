from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    """
    Erlaubt nur Benutzern mit dem Typ 'business', ein Angebot zu erstellen.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated and getattr(request.user, 'type', None) == 'business'
        return True  
