from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsDashboardUser(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return (
            u
            and u.is_authenticated
            and (u.is_superuser or u.groups.filter(name="DashboardAccess").exists())
        )