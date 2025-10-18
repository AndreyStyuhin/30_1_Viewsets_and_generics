from rest_framework import permissions

# Этот класс больше не нужен, его логика перенесена в IsModerOrIsOwner
# class IsModer(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(user and user.is_authenticated and user.groups.filter(name='moderators').exists())

# Этот класс больше не нужен, его логика перенесена в IsModerOrIsOwner
# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return bool(request.user and request.user.is_authenticated and getattr(obj, 'owner', None) == request.user)


class IsModerOrIsOwner(permissions.BasePermission):
    """
    Разрешение, если пользователь является модератором или владельцем объекта.
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли пользователь владельцем объекта
        is_owner = getattr(obj, 'owner', None) == request.user

        # Проверяем, является ли пользователь модератором
        is_moderator = request.user.groups.filter(name='moderators').exists()

        # Разрешаем доступ, если выполняется хотя бы одно из условий
        return request.user.is_authenticated and (is_owner or is_moderator)
