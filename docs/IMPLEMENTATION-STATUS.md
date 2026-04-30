# Статус реализации (док ↔ код)

**Назначение:** один файл, чтобы **критерии пайплайна** ([PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md)) не расходились с фактом в `backend/` и `frontend/`.  
**Как обновлять:** после значимого PR или закрытия подфазы — правь таблицу и блоки ниже; дата в шапке обязательна.

**Последнее обновление:** 2026-04-30.

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
| 6 | Прод + наблюдаемость | **Частично** | `health/`; `GET /api/v1/metrics/` (Prometheus text, **только staff**); бэкапы `infra/scripts/`; в prod при `SENTRY_DSN` — инициализация Sentry (`sentry-sdk` в requirements). Нет полноценного Prometheus/Grafana стека и расширенного incident-runbook. |
| 7 | Штат / партнёр | **Частично** | `EmploymentKind`, `IsInternalEmployeeOrStaff`, `/api/v1/internal/status/`; фронт: маршрут **`/internal`**, пункт меню только для **staff или штатного** сотрудника (`employment_kind === internal`), guard `requiresInternal`. Партнёр не видит пункт и не должен получать 200 с internal API. |
| 8 | Рабочий хаб, канбан | **Частично** | `WorkGroup/Board/Column/Task`, CRUD, **`POST /tasks/columns/reorder/`**, пресеты колонок; UI `/work` с **DnD колонок и задач** (vuedraggable). Нет WS-доски, автоматизаций, расширенных фильтров. **Задел CRM** — по-прежнему опционально вне этого PR. |
| 9 | Админ-панель | **Частично** | Пользователи + PATCH; **каталог разрешений**, **CRUD групп пользователей** (`/admin/permission-groups/`), **компании и отделы** (`/admin/organizations/`, `/admin/departments/`), привязка пользователя к отделу; `effective_permission_slugs` в **`/auth/me/`**. Нет модерации сообществ в UI. |
| 10+ | Соцрасширение | **Частично** | **MVP друзей:** модель `FriendRequest`, API `social/friends`, входящие запросы, accept/reject; страница **`/friends`**. Нет ленты «как ВК», вложений в ленту, пушей, полной модерации — это отдельный объём. |
| 11 | Контейнеризация и CI/CD | **Частично** | Образы + `.dockerignore`, nginx (**прокси `/api/`, `/ws/`**), `docker-compose.stack.yml`, CI: validate compose + сборка образов на PR + GHCR `latest`/`sha` на `main`, deploy SSH на stack; k8s/авто-rollback — вне объёма. |

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

### Фаза 6 (инкремент)

- **Сделано:** `health/`; `GET /api/v1/metrics/` (staff); опционально Sentry в prod (`SENTRY_DSN`); скрипты `infra/scripts/backup_db.sh` и `infra/scripts/restore_db.sh`.
- **Не сделано:** полноценный стек Prometheus/Grafana в compose, расширенный runbook.

### Фаза 7 (инкремент)

- **Сделано:** `accounts.User.employment_kind`, permission `IsInternalEmployeeOrStaff`, endpoint `/api/v1/internal/status/`; фронт **`/internal`**, `requiresInternal`, `canAccessInternalRoute`, пункт меню только для штата/staff; Vitest `internalAccess.spec.ts`.
- **Не сделано:** полный набор internal-only API и виджетов partner vs internal на всех экранах.

### Фаза 8 (инкремент)

- **Сделано:** доменные модели `WorkGroup`, `WorkBoard`, `WorkColumn`, `WorkTask`; API `/tasks/...`, **`POST /tasks/columns/reorder/`**; UI `/work` с DnD (vuedraggable).
- **Не сделано:** realtime WS на доске, автоматизации, расширенный поиск; **лёгкий CRM** — по желанию отдельным PR.

### Фазы 10+

- **Сделано (MVP):** `apps.social` — `FriendRequest`, эндпоинты под `api/v1/social/...`, страница **`/friends`**; pytest `tests/test_pipeline_features.py` (друзья).
- **Не сделано:** персональная лента «как ВК», вложения, пуши, полная модерация.

### Фаза 9

- **Сделано:** `PATCH /admin/users/` (в т.ч. `department`, `permission_group_ids`), аудит; каталог и группы: **`/admin/permission-catalog/`**, **`/admin/permission-groups/`**, организации/отделы; **`effective_permission_slugs`** в `UserPublicSerializer` / `GET /auth/me/`; UI консоли — вкладки пользователи / группы.
- **Не сделано:** модерация сообществ в консоли; тонкая проверка каждого permission slug на всех эндпоинтах (сейчас каталог и группы готовы к поэтапному внедрению).

### Фаза 11

- **Сделано:** `docker-compose.stack.yml`, `stack.env.example`, nginx reverse-proxy для API/WS, `.dockerignore`, healthcheck `api` в dev compose; CI: `compose-validate`, `docker-verify`, push в GHCR с **lowercase** путём и тегами `latest` + `sha`; `deploy.yml` использует stack-файл и smoke через nginx.
- **Не сделано:** fully automated rollback и оркестратор уровня k8s/terraform по enterprise-критерию.

---

## Следующий приоритет (рекомендация)

1. Включить проверки **permission slugs** на критичных API (после каталога групп).  
2. Фаза 8: WS на доске, фильтры, опционально CRM-модели.  
3. Фаза 10+: лента друзей, вложения, уведомления.

Порядок можно менять по продукту; этот файл — только фиксация **факта**, не планирование.
