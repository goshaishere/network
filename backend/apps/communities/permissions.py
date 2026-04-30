from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import CommunityMembership


class CommunityPostWritePermission(BasePermission):
    """PATCH body — автор; PATCH hidden_from_feed — автор или модератор сообщества."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method in ("PATCH", "PUT"):
            keys = set(request.data.keys())
            if not keys.issubset({"body", "hidden_from_feed"}):
                return False
            if "body" in keys and obj.author_id != request.user.id:
                return False
            if "hidden_from_feed" in keys:
                if obj.author_id == request.user.id:
                    return True
                m = CommunityMembership.objects.filter(community=obj.community, user=request.user).first()
                return bool(m and m.role == CommunityMembership.Role.MODERATOR)
            return True
        return False
