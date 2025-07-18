from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """secure methods are available for ordinary users,
    even if they are not authorized, and full access is
    available for superusers and admins"""

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return True
        return False
