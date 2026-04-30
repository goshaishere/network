from apps.console.permissions_catalog import ALL_PERMISSION_SLUGS


def get_effective_permission_slugs(user) -> set[str]:
    """Объединение разрешений групп; staff/superuser — весь каталог."""
    if user.is_anonymous:
        return set()
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return set(ALL_PERMISSION_SLUGS)
    slugs: set[str] = set()
    # related_name permission_groups на M2M members у UserPermissionGroup
    for g in user.permission_groups.all().only("permission_slugs"):
        for s in g.permission_slugs or []:
            if s in ALL_PERMISSION_SLUGS:
                slugs.add(s)
    return slugs
