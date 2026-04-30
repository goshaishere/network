"""Каталог разрешений для групп пользователей (консоль / внутренние инструменты)."""

PERMISSION_CATALOG: list[dict[str, str]] = [
    {"slug": "console.view_users", "name": "Просмотр пользователей"},
    {"slug": "console.edit_users", "name": "Редактирование пользователей и ролей"},
    {"slug": "console.view_audit", "name": "Просмотр журнала аудита"},
    {"slug": "console.manage_groups", "name": "Управление группами и разрешениями"},
    {"slug": "console.manage_org", "name": "Управление компаниями и отделами"},
    {"slug": "internal.tools", "name": "Доступ к внутренним инструментам (по политике продукта)"},
    {"slug": "work.advanced", "name": "Расширенные возможности рабочего контура"},
]

ALL_PERMISSION_SLUGS: frozenset[str] = frozenset(p["slug"] for p in PERMISSION_CATALOG)
