from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        if view.action == 'create':
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
