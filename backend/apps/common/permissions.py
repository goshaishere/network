from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.console.services.permissions import get_effective_permission_slugs


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


class CanScrapeMetrics(BasePermission):
    """Staff или секретный токен (заголовок X-Metrics-Token / query token)."""

    def has_permission(self, request, view):
        token = getattr(settings, "METRICS_SCRAPE_TOKEN", "") or ""
        token = str(token).strip()
        if token:
            if request.headers.get("X-Metrics-Token") == token:
                return True
            qp = getattr(request, "query_params", None)
            if qp is not None and qp.get("token") == token:
                return True
        u = request.user
        if u and u.is_authenticated and getattr(u, "is_staff", False):
            return True
        # View может отключить JWT (authentication_classes = []); тогда staff через Bearer.
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

            auth = JWTAuthentication()
            pair = auth.authenticate(request)
            if pair and getattr(pair[0], "is_staff", False):
                return True
        except (InvalidToken, TokenError):
            pass
        return False


class IsInternalEmployeeOrStaff(BasePermission):
    """Внутренние рабочие API: staff или internal-сотрудник."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if getattr(u, "is_staff", False):
            return True
        if not getattr(u, "is_employee", False):
            return False
        return getattr(u, "employment_kind", "") == "internal"


class RequiresPermissionSlug(BasePermission):
    """
    Проверка доступа по permission slug.

    View может указать:
    - required_permission_slug = "domain.action"
    - required_permission_slug_map = {"GET": "...", "POST": "..."}
    """

    message = "Недостаточно прав для выполнения действия."

    def _resolve_required_slug(self, request, view) -> str | None:
        mapping = getattr(view, "required_permission_slug_map", None) or {}
        if request.method in mapping:
            return mapping[request.method]
        return getattr(view, "required_permission_slug", None)

    def has_permission(self, request, view):
        required_slug = self._resolve_required_slug(request, view)
        if not required_slug:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return required_slug in get_effective_permission_slugs(user)
