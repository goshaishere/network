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
| 5 | Сообщества | **Частично** | Бэк `communities` (создание, join, посты, открытое/закрытое). Фронт — заглушки; **нет** политики «`/work` недоступен обычному user» как в фазе 5. |
| 6 | Прод + наблюдаемость | **Не начато** | Нет prod-деплоя, бэкапов, Sentry/Prometheus по критерию. |
| 7 | Штат / партнёр | **Не начато** | Нет `EmploymentKind`, `/api/v1/internal/...`, скрытия пунктов для partner. |
| 8 | Рабочий хаб, канбан | **Не начато** | Только заглушки `work/dashboard/`, `tasks/groups/`, `tasks/boards/`; нет `WorkGroup`, досок, `semantic`, 403 для `user` на `/work`/tasks API. |
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
- **Сделано (фронт):** `src/composables/useMessagingSocket.ts`, `MessagesListPage.vue`, `ConversationPage.vue` (REST + подписка WS, дедуп по `id`), прокси `vite.config.ts` → `/ws`; кнопка «Написать» с профиля; в списке диалогов — `other_display_name`. Прод: задать `VITE_WS_URL` или проксировать WSS до ASGI.

### Фаза 5

- **Сделано (бэк):** `apps.communities` — список/создание, карточка, join, посты.
- **Не сделано:** фронт списков/карточки; разделение гость vs `user`; **ограничение `/work` только для employee** (сейчас заглушка с `requiresAuth`, не роль).

### Фазы 6–8, 10+

- Нет реализации, соответствующей критериям в `PROJECT-PIPELINE.md` (кроме заглушек под work/tasks в `apps.work`).

### Фаза 9

- Заглушки под `admin/users`, `admin/roles`; полноценной консоли по критерию нет.

---

## Следующий приоритет (рекомендация)

1. **Фаза 5:** UI сообществ + guards **`employee`** для `/work` и API задач (подготовка к фазе 8).  
2. **Улучшения фазы 3:** `useDashboardLayout`, DnD-сетка, виджеты по ролям.  
3. **Улучшения фазы 4:** переподключение WS при refresh токена, индикатор «печатает…», доставка офлайн.

Порядок можно менять по продукту; этот файл — только фиксация **факта**, не планирование.
