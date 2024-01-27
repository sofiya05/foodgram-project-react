from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthorizedOwnerOrReadOnly(BasePermission):
    message = (
        'Учетные данные не были предоставлены или вы '
        'не являетесь автором рецепта.'
    )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            obj.author == request.user
        )
