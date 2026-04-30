"""Персональная лента: стены (я + друзья с публичным профилем) + посты сообществ, где пользователь состоит."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Q

from apps.communities.models import CommunityMembership, CommunityPost
from apps.profiles.models import Profile
from apps.walls.models import WallPost

from .models import FriendRequest

PAGE_SIZE = 15
MAX_WALL_FETCH = 200
MAX_COMM_FETCH = 200
MAX_MERGED = MAX_WALL_FETCH + MAX_COMM_FETCH


def _accepted_friend_ids(user) -> set[int]:
    out: set[int] = set()
    for r in FriendRequest.objects.filter(
        status=FriendRequest.Status.ACCEPTED,
    ).filter(Q(from_user=user) | Q(to_user=user)):
        oid = r.to_user_id if r.from_user_id == user.id else r.from_user_id
        out.add(oid)
    return out


def _wall_owner_ids_for_feed(user) -> set[int]:
    """Владельцы стен, чьи посты попадают в ленту (с учётом приватности профиля)."""
    ids: set[int] = {user.id}
    for fid in _accepted_friend_ids(user):
        prof = Profile.objects.filter(user_id=fid).first()
        if prof and prof.privacy == Profile.Privacy.PRIVATE:
            continue
        ids.add(fid)
    return ids


def _member_community_ids(user) -> list[int]:
    return list(
        CommunityMembership.objects.filter(user=user).values_list("community_id", flat=True).distinct()
    )


@dataclass
class _Merged:
    kind: str  # "wall" | "community"
    created_at: Any
    sort_id: int
    obj: WallPost | CommunityPost


def _merge_posts(wall_posts: list[WallPost], comm_posts: list[CommunityPost]) -> list[_Merged]:
    rows: list[_Merged] = []
    for p in wall_posts:
        rows.append(_Merged("wall", p.created_at, p.id, p))
    for p in comm_posts:
        rows.append(_Merged("community", p.created_at, p.id, p))
    rows.sort(
        key=lambda r: (r.created_at, 0 if r.kind == "wall" else 1, r.sort_id),
        reverse=True,
    )
    return rows[:MAX_MERGED]


def build_feed_page(user, offset: int = 0) -> tuple[list[dict[str, Any]], int | None]:
    """
    Возвращает (результаты, next_offset или None).
    offset — смещение в объединённом списке (не более MAX_MERGED элементов).
    """
    if offset < 0:
        offset = 0
    wall_owners = _wall_owner_ids_for_feed(user)
    wall_qs = (
        WallPost.objects.filter(wall_owner_id__in=wall_owners)
        .select_related("author", "wall_owner")
        .order_by("-created_at")[:MAX_WALL_FETCH]
    )
    comm_ids = _member_community_ids(user)
    comm_qs = (
        CommunityPost.objects.filter(community_id__in=comm_ids)
        .select_related("author", "community")
        .order_by("-created_at")[:MAX_COMM_FETCH]
    )
    merged = _merge_posts(list(wall_qs), list(comm_qs))
    end = offset + PAGE_SIZE
    slice_rows = merged[offset:end]
    next_off: int | None = offset + len(slice_rows) if offset + len(slice_rows) < len(merged) else None

    results: list[dict[str, Any]] = []
    for m in slice_rows:
        if m.kind == "wall":
            p = m.obj
            assert isinstance(p, WallPost)
            results.append(
                {
                    "type": "wall",
                    "id": p.id,
                    "created_at": p.created_at,
                    "body": p.body,
                    "wall_owner_id": p.wall_owner_id,
                    "author_id": p.author_id,
                    "author_display_name": p.author.display_name or "",
                    "wall_owner_display_name": p.wall_owner.display_name or "",
                }
            )
        else:
            p = m.obj
            assert isinstance(p, CommunityPost)
            results.append(
                {
                    "type": "community",
                    "id": p.id,
                    "created_at": p.created_at,
                    "body": p.body,
                    "community_id": p.community_id,
                    "community_slug": p.community.slug,
                    "community_name": p.community.name,
                    "author_id": p.author_id,
                    "author_display_name": p.author.display_name or "",
                }
            )
    return results, next_off
