from rest_framework import permissions


class IsSuperAdminForUpdate(permissions.BasePermission):
    def has_permission(self, request, view):
        # everyone can see list of roles
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request so we'll always
        # allow GET, HEAD, or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to staff memmbers
        return request.user.is_super_admin
