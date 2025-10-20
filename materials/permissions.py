# ФАЙЛ: materials/permissions.py (Воссоздан на основе тестов)

from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    """
    Права доступа для модератора.
    Модератор (группа 'moderators') имеет доступ.
    """
    message = 'Вы не являетесь модератором.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='moderators').exists()

class IsOwner(BasePermission):
    """
    Права доступа для владельца объекта.
    Владелец (obj.owner) имеет доступ.
    """
    message = 'Вы не являетесь владельцем.'

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.owner == request.user