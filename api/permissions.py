"""
RESTful API Module - Custom Permissions

Custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Permission check for staff or admin role
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'profile'):
            return False

        return request.user.profile.is_staff() or request.user.profile.is_admin()


class IsPatientOwner(permissions.BasePermission):
    """
    Permission check for patient accessing their own data
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Check if user is the owner
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Admins and staff have read access to all objects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'patient'):
            return obj.patient.user == request.user

        return False
