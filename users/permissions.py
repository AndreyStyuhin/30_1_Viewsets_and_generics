from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Разрешение, если пользователь входит в группу 'moderators'"""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name='moderators').exists())


class IsOwner(permissions.BasePermission):
    """Разрешение на основе наличия атрибута owner у объекта"""

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and getattr(obj, 'owner', None) == request.user)