"""Модуль кастомных разрешений"""
from rest_framework import permissions


class PartyOwner(permissions.BasePermission):
    """
    Кастомное разрешение для действий над мероприятиями
    Просмотр мероприятий доступен любому авторизованному пользователю.
    Действия над мероприятиями доступны владельцам мероприятий или суперпользователю
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or obj.user == request.user:
            return True
        return False


class IsSuperUser(permissions.BasePermission):
    """
    Кастомное разрешение для Суперпользователя
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return False
