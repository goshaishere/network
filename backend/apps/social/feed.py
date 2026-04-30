"""Персональная лента: стены (я + друзья с публичным профилем) + посты сообществ; слияние потоков без жёсткого лимита."""

from __future__ import annotations

import heapq
from typing import Any, Iterator

from django.db.models import Q

from apps.communities.models import CommunityMembership, CommunityPost
from apps.profiles.models import Profile
from apps.walls.models import WallPost

from .models import FriendRequest

PAGE_SIZE = 15


def _accepted_friend_ids(user) -> set[int]:
    out: set[int] = set()
    for r in FriendRequest.objects.filter(
        status=FriendRequest.Status.ACCEPTED,
    ).filter(Q(from_user=user) | Q(to_user=user)):
        oid = r.to_user_id if r.from_user_id == user.id else r.from_user_id
        out.add(oid)
    return out


def _wall_owner_ids_for_feed(user) -> set[int]:
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


def _neg_stream_wall(qs) -> Iterator[tuple[float, int, str, WallPost]]:
    for ob in qs.iterator(chunk_size=400):
        yield (-ob.created_at.timestamp(), -ob.id, "wall", ob)


def _neg_stream_community(qs) -> Iterator[tuple[float, int, str, CommunityPost]]:
    for ob in qs.iterator(chunk_size=400):
        yield (-ob.created_at.timestamp(), -ob.id, "community", ob)


def _attachment_url(request, uf) -> str:
    if not uf or not uf.file:
        return ""
    url = uf.file.url
    if request:
        return request.build_absolute_uri(url)
    return url


def _serialize_wall(request, p: WallPost) -> dict[str, Any]:
    return {
        "type": "wall",
        "id": p.id,
        "created_at": p.created_at,
        "body": p.body,
        "wall_owner_id": p.wall_owner_id,
        "author_id": p.author_id,
        "author_display_name": p.author.display_name or "",
        "wall_owner_display_name": p.wall_owner.display_name or "",
        "attachment_url": _attachment_url(request, getattr(p, "uploaded_file", None)),
        "hidden_from_feed": p.hidden_from_feed,
    }


def _serialize_community(request, p: CommunityPost) -> dict[str, Any]:
    return {
        "type": "community",
        "id": p.id,
        "created_at": p.created_at,
        "body": p.body,
        "community_id": p.community_id,
        "community_slug": p.community.slug,
        "community_name": p.community.name,
        "author_id": p.author_id,
        "author_display_name": p.author.display_name or "",
        "attachment_url": _attachment_url(request, getattr(p, "uploaded_file", None)),
        "hidden_from_feed": p.hidden_from_feed,
    }


def build_feed_page(user, offset: int = 0, request=None) -> tuple[list[dict[str, Any]], int | None]:
    """
    Слияние двух отсортированных потоков (heapq.merge), пагинация по offset.
    Посты с hidden_from_feed=True не попадают в ленту.
    """
    if offset < 0:
        offset = 0
    wall_owners = _wall_owner_ids_for_feed(user)
    comm_ids = _member_community_ids(user)

    streams: list[Iterator[tuple[float, int, str, Any]]] = []
    if wall_owners:
        wq = (
            WallPost.objects.filter(wall_owner_id__in=wall_owners, hidden_from_feed=False)
            .select_related("author", "wall_owner", "uploaded_file")
            .order_by("-created_at", "-id")
        )
        streams.append(_neg_stream_wall(wq))
    if comm_ids:
        cq = (
            CommunityPost.objects.filter(community_id__in=comm_ids, hidden_from_feed=False)
            .select_related("author", "community", "uploaded_file")
            .order_by("-created_at", "-id")
        )
        streams.append(_neg_stream_community(cq))

    if not streams:
        return [], None

    merged = heapq.merge(*streams)

    results: list[dict[str, Any]] = []
    skipped = 0
    for _neg_ts, _neg_id, kind, obj in merged:
        if skipped < offset:
            skipped += 1
            continue
        if len(results) >= PAGE_SIZE:
            break
        if kind == "wall":
            results.append(_serialize_wall(request, obj))
        else:
            results.append(_serialize_community(request, obj))

    next_off: int | None = offset + len(results) if len(results) == PAGE_SIZE else None
    return results, next_off
