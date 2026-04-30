from rest_framework.permissions import SAFE_METHODS, BasePermission


class WallPostWritePermission(BasePermission):
    """DELETE — только автор; PATCH body — автор; PATCH hidden_from_feed — автор или владелец стены."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method == "DELETE":
            return obj.author_id == request.user.id
        if request.method in ("PATCH", "PUT"):
            keys = set(request.data.keys())
            if not keys.issubset({"body", "hidden_from_feed"}):
                return False
            if "body" in keys and obj.author_id != request.user.id:
                return False
            if "hidden_from_feed" in keys and request.user.id not in (
                obj.author_id,
                obj.wall_owner_id,
            ):
                return False
            return True
        return False
