# Статус реализации (док ↔ код)

**Назначение:** один файл, чтобы **критерии пайплайна** ([PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md)) не расходились с фактом в `backend/` и `frontend/`.  
**Как обновлять:** после значимого PR или закрытия подфазы — правь таблицу и блоки ниже; дата в шапке обязательна.

**Последнее обновление:** 2026-04-24.

---

## Сводная таблица

| Фаза | Кратко | Статус | Примечание |
|------|--------|--------|------------|
| 0 | Документация | **Готово** | Чеклисты в пайплайне `[x]` соответствуют наличию `docs/`. |
| 1 | Каркас репо | **Готово** | Django split settings, DRF, JWT, CORS, ASGI+Channels+Redis, Quasar+Vite+TS+i18n+тема, compose, CI. |
| 2 | Auth и вход | **Готово** | JWT, blacklist, `me`, сброс пароля; hCaptcha после N ошибок (`captcha_required`), кэш счётчика, `ScopedRateThrottle` на login и сброс пароля; фронт передаёт `captcha_token`, виджет hCaptcha. |
| 3 | Профиль, стена, `/`, дашборд | **Готово** | Лёгкая главная `/` (превью стены и диалогов, быстрые ссылки), `/dashboard` с виджетами и PATCH layout, профиль/стена, настройки `profiles/me`. Drag-and-drop сетка и расширенный каталог виджетов по ролям — позже (см. ROLES §5.2). |
| 4 | ЛС MVP | **Готово** | REST + WS; фронт: `MessagesListPage`, `ConversationPage`, `useMessagingSocket` (JWT в query, subscribe), Vite proxy `/ws`, входящие без F5; `other_display_name` в списке диалогов. |
| 5 | Сообщества + доступ к `/work` | **Готово** | Бэк `communities` + фронт `CommunitiesListPage` / `CommunityDetailPage` (лента, join, посты). **`User.is_employee`**, `IsEmployeeOrStaff` на `work/` и tasks stubs; фронт `requiresEmployee`, «Работа» в сайдбаре только staff/employee. |
| 6 | Прод + наблюдаемость | **Не начато** | Нет prod-деплоя, бэкапов, Sentry/Prometheus по критерию. |
| 7 | Штат / партнёр | **Не начато** | Нет `EmploymentKind`, `/api/v1/internal/...`, скрытия пунктов для partner. |
| 8 | Рабочий хаб, канбан | **Частично** | Заглушки `work/dashboard/`, `tasks/groups/`, `tasks/boards/`; **403/401** для обычного `user` без `is_employee`/staff — **есть**. Нет `WorkGroup`, досок, `semantic`, полноценного канбана. |
| 9 | Админ-панель | **Частично** | `GET admin/users/`, `GET admin/roles/` (заглушка); нет назначения ролей, EmploymentKind, оргструктуры из критерия. |
| 10+ | Соцрасширение | **Не начато** | — |

Легенда: **Готово** — критерий фазы в целом выполнен; **Частично** — есть инкремент, критерий нет; **Не начато** — нет содержательной реализации.

---

## Детализация по фазам (привязка к коду)

### Фаза 1

- **Сделано:** `backend/config/settings/`, DRF+SimpleJWT+CORS, `daphne`+`channels`+`channels-redis`, `docker-compose.yml`, `frontend/` (Quasar, роутер, guards, i18n), `.github/workflows/ci.yml`.
- **Проверка:** локально `pytest`, `npm run build`; CI — см. workflow.

### Фаза 2

- **Сделано:** `apps.accounts` — register/login/refresh/logout/me/password reset; кэш и порог `LOGIN_CAPTCHA_THRESHOLD`, `verify_hcaptcha_response`, ответ `CaptchaRequired` (`code: captcha_required`); `ScopedRateThrottle` для `login`, `password_reset`, `password_reset_confirm`; фронт — `captcha_token`, виджет `@hcaptcha/vue3-hcaptcha`, `VITE_HCAPTCHA_SITEKEY`.
- **Опционально позже:** отдельный Redis только для кэша при необходимости масштабирования (сейчас prod — Redis DB `/2`, local — LocMem).

### Фаза 3

- **Сделано (API):** `apps.profiles`, `apps.walls`; эндпоинты из [BACKEND.md](./BACKEND.md) для профиля, стены, `profiles/me/dashboard/`.
- **Сделано (UI):** «лёгкая главная» [ROLES §5.1](./ROLES-AND-TASKS.md): превью стены и диалогов, ссылки на сообщества/сообщения/дашборд; `DashboardPage`, `UserProfilePage`, `SettingsProfilePage`, `author_display_name` на стене.
- **Позже (§5.2):** drag-and-drop сетка, каталог виджетов по ролям, `useDashboardLayout` как отдельный composable.

### Фаза 4

- **Сделано (бэк):** `apps.messaging`, `ws/messaging/?token=`, `MessagingConsumer`, `broadcast_new_message` в группу `conversation_{id}`.
- **Сделано (фронт):** `src/composables/useMessagingSocket.ts`, `MessagesListPage.vue`, `ConversationPage.vue` (REST + подписка WS, дедуп по `id`), прокси `vite.config.ts` → `/ws`; кнопка «Написать» с профиля; в списке диалогов — `other_display_name`. При **refresh JWT** (`tokenGeneration` в Pinia) — переподключение WS; ошибки загрузки/отправки в UI; `Notify` в Quasar. Прод: задать `VITE_WS_URL` или проксировать WSS до ASGI.
- **Сделано (надёжность):** `broadcast_new_message` не роняет `POST` при недоступном Redis — лог + продолжение; pytest: `config.settings.test` + InMemory channel layer, принудительно в `tests/conftest.py`; см. `tests/test_messaging.py`.

### Фаза 5

- **Сделано (бэк):** `apps.communities` — список/создание, карточка (`members_count`, `is_member`), join, посты; `apps.accounts` — **`is_employee`**; `apps.common.permissions.IsEmployeeOrStaff`; `apps.work` — dashboard и tasks stubs только для staff или `is_employee`.
- **Сделано (фронт):** `CommunitiesListPage`, `CommunityDetailPage`; `WorkHubPage`, meta **`requiresEmployee`**, guard; пункт «Работа» в `MainSidebar` при `is_staff || is_employee`; `AuthUser.is_employee` в store и i18n.
- **Позже:** тонкая политика «что видит гость vs user» на уровне отдельных экранов сообществ (сейчас — по возможностям API: без токена — только публичные чтения где разрешено DRF).

### Фаза 8 (инкремент)

- **Сделано:** доступ к заглушкам work/tasks по роли (см. фазу 5 в таблице).
- **Не сделано:** доменные модели рабочего хаба, канбан, `semantic` — по критерию пайплайна.

### Фазы 6–7, 10+

- Нет реализации, соответствующей критериям в `PROJECT-PIPELINE.md`.

### Фаза 9

- Заглушки под `admin/users`, `admin/roles`; полноценной консоли по критерию нет.

---

## Следующий приоритет (рекомендация)

1. **Фаза 8:** `WorkGroup`, доски, канбан, `semantic`, расширение API поверх текущих заглушек.  
2. **Улучшения фазы 3:** `useDashboardLayout`, DnD-сетка, виджеты по ролям.  
3. **Улучшения фазы 4:** индикатор «печатает…», доставка офлайн (переподключение WS при refresh — уже учтено в фазе 4 в таблице выше).

Порядок можно менять по продукту; этот файл — только фиксация **факта**, не планирование.
