from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permissão para apenas administradores"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permissão para admins editarem e outros apenas lerem"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOperadorOrAdmin(permissions.BasePermission):
    """Permissão para operadores e administradores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_operador)
        )
