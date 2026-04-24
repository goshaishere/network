# Backend: Django 6 + DRF

## 1. Цели API

- **Лаконичные** ресурсы: имена существительных, глаголы только где уместно (например `login`).  
- Версионирование: префикс `/api/v1/` (или заголовок — выбрать один способ и не смешивать).  
- Единый формат ошибок: `{ "detail": "..." }` или `{ "field": ["..."] }` в стиле DRF.

## 2. Аутентификация (зафиксировано: JWT)

- **`djangorestframework-simplejwt`**: пара **access** (короткий TTL) + **refresh** (длиннее).  
- REST: заголовок `Authorization: Bearer <access>`.  
- **Refresh:** либо `POST /api/v1/auth/token/refresh/` с телом `{ "refresh": "..." }`, либо refresh в **httpOnly cookie** (сильнее против XSS, сложнее CSRF — настраивается отдельно).  
- **Logout:** `rest_framework_simplejwt.token_blacklist` — занесение refresh в blacklist (если храните refresh на сервере).  
- Логин с капчей: кастомный view (наследник или обёртка над `TokenObtainPairView`) — сначала проверки капчи/счётчика, затем стандартная выдача JWT.

## 3. Предлагаемые эндпоинты (черновик контракта)

Группа **auth** (часть без токена, часть с токеном):

| Метод | Путь | Назначение |
|--------|------|------------|
| POST | `/api/v1/auth/register/` | Регистрация → при желании сразу access/refresh |
| POST | `/api/v1/auth/login/` | Логин → access + refresh (+ `captcha_required` при превышении порога) |
| POST | `/api/v1/auth/token/refresh/` | Новый access (и ротация refresh — по настройке SimpleJWT) |
| POST | `/api/v1/auth/logout/` | Blacklist refresh / очистка cookie |
| GET | `/api/v1/auth/me/` | Текущий пользователь (Bearer access) |
| POST | `/api/v1/auth/password/reset/request/` | Запрос письма |
| POST | `/api/v1/auth/password/reset/confirm/` | Новый пароль по uid/token |

**Профиль и стена:**

| Метод | Путь | Назначение |
|--------|------|------------|
| GET/PATCH | `/api/v1/profiles/me/` | Свой профиль и настройки |
| GET/PATCH | `/api/v1/profiles/me/dashboard/` | Раскладка виджетов **`/dashboard`** (JSON + валидация типов по роли) |
| GET | `/api/v1/profiles/{user_id}/` | Публичный профиль (с учётом приватности) |
| GET | `/api/v1/walls/{user_id}/posts/` | Лента стены |
| POST | `/api/v1/walls/{user_id}/posts/` | Новый пост на стене (права в сервисе) |
| PATCH/DELETE | `/api/v1/walls/posts/{id}/` | Редактирование / удаление своего поста |

**Сообщества** (роль `user+`, не путать с рабочими группами):

| Метод | Путь | Назначение |
|--------|------|------------|
| GET/POST | `/api/v1/communities/` | Список / создание |
| GET/PATCH | `/api/v1/communities/{slug}/` | Карточка, настройки (модераторы) |
| POST | `/api/v1/communities/{slug}/join/` | Вступить |
| GET/POST | `/api/v1/communities/{slug}/posts/` | Лента сообщества |

**Сообщения:**

| Метод | Путь | Назначение |
|--------|------|------------|
| GET | `/api/v1/messaging/conversations/` | Список диалогов |
| POST | `/api/v1/messaging/conversations/` | Создать диалог (или получить существующий 1-1) |
| GET | `/api/v1/messaging/conversations/{id}/messages/` | История с курсором |
| POST | `/api/v1/messaging/conversations/{id}/messages/` | Отправить сообщение (запись в БД + broadcast в WS-группу) |

**WebSocket (не JSON в таблице URL — см. `routing.py`):**

| Протокол | Путь (пример) | Назначение |
|----------|----------------|------------|
| WS | `wss://api.example.com/ws/messaging/` | Аутентификация JWT (query `token=` **только по WSS** или отдельный **ws_ticket** — зафиксировать при коде), подписка на события диалогов пользователя |

**Служебное:**

| Метод | Путь | Назначение |
|--------|------|------------|
| POST | `/api/v1/media/` | Загрузка файла (multipart), ответ `{ "url", "id" }` |

Имена и глубина вложенности можно упростить до плоских URL при реализации — главное зафиксировать в OpenAPI.

## 4. Классы и файлы по приложениям

### `config`

- `settings/base.py`, `local.py`, `production.py` — разделение окружений.  
- `urls.py` — подключение `include("apps.accounts.urls"))` и т.д.  
- `asgi.py` — **точка входа для production**: Daphne/Uvicorn; подключение `ProtocolTypeRouter` (HTTP Django + WebSocket Channels).  
- `wsgi.py` — опционально для совместимости; целевой режим — **ASGI**.

### `apps.common`

- `pagination.py` — `CursorPagination` или `PageNumberPagination`.  
- `permissions.py` — например `IsOwnerOrReadOnly`.  
- `exceptions.py` — при необходимости кастомный handler 400/403/404.

### `apps.accounts`

| Файл | Классы / сущности |
|------|-------------------|
| `models.py` | Расширение пользователя при необходимости; `LoginAttempt` (ip, username, fails, window) — или хранение в кэше |
| `serializers.py` | `RegisterSerializer`, `LoginSerializer`, `PasswordResetRequestSerializer`, … |
| `views.py` / `views/` | `RegisterView`, `LoginView`, … |
| `services/auth.py` | `authenticate_and_issue_pair()`, `register_user()`, проверка **hCaptcha** |
| `throttles.py` | Кастомные throttle для login/reset |
| `admin.py` | Модерация пользователей |

### `apps.profiles`

| Файл | Назначение |
|------|------------|
| `models.py` | `Profile`: bio, avatar, locale, privacy; **`dashboard_layout`**, **`default_landing`**; поля сотрудника (компания/отдел/должность) |
| `serializers.py` | Публичный vs приватный сериализатор |
| `views.py` | `ProfileMeView`, `ProfileDetailView`, **`DashboardLayoutView`** (`GET/PATCH .../me/dashboard/`) |
| `services/profile.py` | Обновление профиля, проверка видимости полей |

### `apps.walls`

| Файл | Назначение |
|------|------------|
| `models.py` | `Post` (wall_owner, author, text, created_at, edited_at) |
| `serializers.py` | `PostSerializer`, create/update |
| `views.py` | `WallPostListCreateView`, `PostDetailView` |
| `services/wall.py` | Кто может постить на чью стену |

### `apps.communities`

| Файл | Назначение |
|------|------------|
| `models.py` | `Community` (slug, тип открытости), `CommunityMembership`, посты сообщества |
| `serializers.py` | Список, деталь, посты |
| `views.py` | ViewSets; права: членство для закрытых, модерация |
| `permissions.py` | Просмотр публичного / только участники |

### `apps.messaging`

| Файл | Назначение |
|------|------------|
| `models.py` | `Conversation`, `Message`, M2M участников или отдельная `Membership` |
| `serializers.py` | Список диалогов, сообщение, создание |
| `views.py` | ViewSets с `get_queryset()` строго по участнику |
| `consumers.py` | Класс(ы) `AsyncJsonWebsocketConsumer`: join групп `user_{id}`, `conversation_{id}`, рассылка событий |
| `routing.py` | `URLRouter` для путей WS |
| `services/messaging.py` | Создание 1-1 беседы, сохранение сообщения, **вызов `channel_layer.group_send`** после `POST` |

После сохранения сообщения в БД сервис публикует событие в Redis channel layer, consumer доставляет его клиентам в комнате.

## 5. Капча и «не с первого раза»

- Сервер хранит **счётчик неудачных попыток** по `(ip, username)` в Redis или в БД с TTL-окном (например 15 минут).  
- Пока счётчик `< 3` — капча не требуется.  
- При `>= 3` — ответ 400 с кодом `captcha_required`; следующий запрос должен включать валидный `captcha_token`.  
- После **успешного** логина счётчик сбрасывается.

**Провайдер (зафиксировано): [hCaptcha](https://www.hcaptcha.com/)** — явный challenge для сценария после нескольких ошибок входа. Ключи: секрет на бэке (`HCAPTCHA_SECRET_KEY`), sitekey на фронте (`VITE_HCAPTCHA_SITEKEY`).

## 6. Тесты

- **Обязательное** покрытие критичных сценариев + прогон в CI: см. **[TESTING.md](./TESTING.md)**.  
- Стек: **`pytest`** + **`pytest-django`**, фабрики **`factory_boy`**, **`pytest-cov`**.  
- Минимум по продукту: auth (JWT + refresh), RBAC (роли и 403), стена, сообщения, задачи/канбан, по возможности **Channels** через `channels.testing` / async-тесты.  
- Допустим встроенный `TestCase` для простых случаев; для нового кода предпочтительно **pytest**-стиль.

## 7. Документация API

- `drf-spectacular` → OpenAPI 3 + UI (Swagger/Redoc) за флагом `DEBUG` или отдельный internal route.

## 8. Роли, сообщества, рабочий контур и админка

- **Сообщества:** `IsAuthenticated` (и проверки членства для закрытых) — см. таблицу выше и [ROLES-AND-TASKS.md](./ROLES-AND-TASKS.md) §2.  
- **Работа:** `IsEmployee`, `IsAdmin`, участник **`WorkGroup`**; префикс `/api/v1/tasks/...` — группы, доски, `preset`, `columns.semantic`, задачи.  
- **Штат vs партнёр:** permission **`IsInternalStaff`** на префикс **`/api/v1/internal/...`** (только `EmploymentKind.internal`); партнёр — только выданные рабочие группы и без внутренних модулей.  
- **`GET /api/v1/work/dashboard/`** (черновик) — агрегаты для главной `/work`.  
- **Админка:** `/api/v1/admin/...`, роль `admin`.  
- Сервисы: `tasks/services/board.py`, `tasks/services/columns.py` (пресеты и единый перечень `semantic` — §6 в ROLES-AND-TASKS).
