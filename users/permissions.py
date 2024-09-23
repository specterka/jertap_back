from rest_framework import permissions


class IsVisitor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_visitor


class IsOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_cafe_owner or request.user.is_cafe_manager)


class IsRestaurantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_cafe_owner

    # def has_object_permission(self, request, view, obj):
    #     return request.user == obj.owner


class IsRestaurantManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_cafe_owner

    # def has_object_permission(self, request, view, obj):
    #     return request.user == obj.manager
