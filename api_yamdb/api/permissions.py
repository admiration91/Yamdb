from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Пользователь имеет роль администратора.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin()
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Пользователь имеет роль администратора.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated
                and request.user.is_admin())
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """
    Пользователь имеет роль администратора, модератора или явялется автором
    объекта.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin()
            or request.user.is_moderator()
        )
