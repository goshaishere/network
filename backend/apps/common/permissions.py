from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Запись только владельцу объекта (obj.user или obj.author)."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        owner = getattr(obj, "user", None) or getattr(obj, "author", None)
        return owner == user


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_staff)


class IsEmployeeOrStaff(BasePermission):
    """Рабочий контур: сотрудник или админ (staff)."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if getattr(u, "is_staff", False):
            return True
        return bool(getattr(u, "is_employee", False))
