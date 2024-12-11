from rest_framework.permissions import BasePermission

class IsParent(BasePermission):
    """
    Custom permission to allow only parents to access a view.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'Parent')

class IsBabysitter(BasePermission):
    """
    Custom permission to allow only babysitters to access a view.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'Babysitter')