# Frontend: Quasar 2 + Vue 3 + Vite + TypeScript

## 1. Принципы

- **Composition API** + `<script setup>` — «современный TS на хуках».  
- Повторяющаяся логика — в **`composables/`** (`useXxx`), не в копипасте страниц.  
- Глобальное состояние сессии — **Pinia** (официально рекомендуется с Vue 3).  
- Стили: **SCSS** (переменные темы + Quasar CSS variables).

## 2. Структура `src/` (целевая)

```
src/
  App.vue
  router/
    index.ts
    routes.ts
    guards.ts              # beforeEach: auth, guest, title
  layouts/
    MainLayout.vue         # шапка, drawer, responsive
    AuthLayout.vue         # центрированные формы
    MinimalLayout.vue      # пустой фон для спец-страниц
  pages/
    auth/
      SignUpPage.vue
      SignInPage.vue
      PasswordResetRequestPage.vue
      PasswordResetConfirmPage.vue
    ErrorNotFound.vue      # 404
    HomeFeedPage.vue       # / или /feed — лёгкая соцглавная (см. ROLES-AND-TASKS §5.1)
    dashboard/
      DashboardPage.vue    # /dashboard — виджеты, режим правки, pin
      widgets/             # виджеты по типам (tasks_due, communities_summary, …)
    communities/
      CommunitiesIndexPage.vue
      CommunityDetailPage.vue
    profile/
      UserProfilePage.vue  # чужой/свой профиль + стена
    settings/
      ProfileSettingsPage.vue
    messaging/
      MessagesIndexPage.vue
      ConversationPage.vue
    work/                    # только employee | admin (guard)
      WorkHomePage.vue         # /work — дашборд работы
      GroupsIndexPage.vue      # рабочие группы (WorkGroup)
      GroupDetailPage.vue
      TasksIndexPage.vue
      BoardPage.vue            # канбан; пресеты колонок — см. ROLES-AND-TASKS §7
    console/                 # только admin
      UsersPage.vue
      RolesPage.vue
  composables/
    useDashboardLayout.ts  # layout /dashboard: API, режим правки, pin
    useApi.ts              # axios instance, baseURL из env
    useAuth.ts             # login, logout, register, JWT access/refresh
    useCaptcha.ts          # hCaptcha: показ виджета, токен для формы
    useMessagingSocket.ts # WebSocket: reconnect, merge в Pinia
    useQuasarTheme.ts      # sync с Pinia + localStorage
    useValidation.ts       # общие правила Quasar / zod
    usePermissions.ts      # роль + employment_kind (internal | partner) из me
  stores/
    auth.ts
    ui.ts                  # sidebar, locale, dark mode
  boot/
    i18n.ts
    axios.ts
  i18n/
    ru-RU/
    en-US/
  css/
    app.scss
    quasar.variables.scss
  components/              # по доменам: auth/, wall/, chat/
  test/                    # или tests/: Vitest + Vue Test Utils (см. TESTING.md)
```

## 3. Лейауты и адаптив

- **MainLayout:** `QHeader`, `QDrawer` (breakpoint: на мобильных overlay, на десктопе side), `QPageContainer`.  
- **AuthLayout:** одна колонка, max-width, карточка `QCard`.  
- Использовать **Quasar breakpoints** (`$q.screen`) и классы `col-xs-12 col-md-8` и т.д.

## 4. Темы: светлая / тёмная

- Включить **Dark plugin** Quasar.  
- Переключатель в шапке или настройках → `Dark.set(bool)` + сохранение в `localStorage`.  
- Кастомные цвета в `quasar.variables.scss` и при необходимости два набора CSS variables.

## 5. Локализация (ru / en)

- **Vue I18n** (стандарт для Quasar).  
- Файлы: `src/i18n/ru-RU/index.ts`, `en-US/index.ts`.  
- Язык по умолчанию из браузера с fallback на `ru-RU`; сохранение выбора в `localStorage`.  
- Ключи вида `auth.signIn.title` для предсказуемости.

## 6. Страницы и маршруты

| Страница | Маршрут (пример) | Кто / заметки |
|-----------|------------------|---------------|
| Соцглавная (лёгкая) | `/` или `/feed` | фиксированные блоки + ссылки; **не** конструктор виджетов |
| **Дашборд** | `/dashboard` | все; **настраиваемые** виджеты, pin, см. ROLES-AND-TASKS §5.2 |
| Регистрация | `/auth/sign-up` | гость |
| Вход | `/auth/sign-in` | гость; hCaptcha с 3-й ошибки |
| Сброс пароля | `/auth/password-reset`, `/confirm` | гость / по ссылке |
| **Сообщества** | `/communities`, `/communities/:slug` | **`user+`** (не требует `employee`) |
| Профиль + стена | `/u/:userId` и т.д. | все |
| Настройки | `/settings/profile` | свой аккаунт |
| Сообщения | `/messages`, `/messages/:id` | все |
| **Работа — главная** | `/work` | только **`employee`**, **`admin`**; для `internal` — расширенные блоки (см. ROLES-AND-TASKS) |
| Рабочие группы | `/work/groups`, `/work/groups/:id` | `employee+` |
| Задачи / канбан | `/work/tasks`, `/work/boards/:id` | `employee+`; участник группы |
| Админ-панель | `/console/...` | `admin` |
| 404 | `/:pathMatch(.*)*` | все |

**Меню MainLayout:** «Главная» (`/` или `/feed`), **«Дашборд»** (`/dashboard`) — у всех залогиненных; «Сообщества», «Сообщения»; «Работа» — только `employee` / `admin`. **`/work`** и **`/console`** — `meta.roles` + **`employment_kind`** в `me` для партнёров.

Доступ к **рабочей** группе/доске — по API (не участник → 403).

## 7. Валидация форм

- **Quasar rules** для простых полей + общие composable-правила (`useValidation`: required, email, min length).  
- Опционально **Zod** + парсинг перед отправкой — единый источник правды для сложных форм.

## 8. API-клиент и JWT

- `axios.create({ baseURL: import.meta.env.VITE_API_URL })`.  
- Request interceptor: `Authorization: Bearer <access>`.  
- Response interceptor: на **401** — один раз `POST .../token/refresh/` (refresh из body или из **httpOnly cookie** — как договоритесь), обновить access, **повторить** исходный запрос; при неудаче — logout и редирект на `/auth/sign-in`.  
- **Access** не класть в `localStorage` при параноидальном уровне — рассмотреть память + refresh cookie; для MVP часто access в памяти Pinia + переживает F5 через refresh в cookie или короткая сессия с повторным логином.  
- Централизованная обработка ошибок (notify через Quasar).

**Переменные окружения (пример):** `VITE_API_URL`, `VITE_WS_URL` (база для `new WebSocket(...)`), `VITE_HCAPTCHA_SITEKEY`.

## 9. Капча на клиенте (hCaptcha)

- При коде `captcha_required` с бэка монтировать виджет **hCaptcha** (`VITE_HCAPTCHA_SITEKEY`).  
- В теле повторного логина передавать `captcha_token` (response от hCaptcha).

## 9a. WebSocket для ЛС

- Один composable `useMessagingSocket`: при авторизации открыть соединение к `VITE_WS_URL`, обработать `onmessage`, обновить Pinia (`messages`, `conversations`).  
- **Reconnect** с backoff при обрыве и при **рестарте сервера** (сокет всегда рвётся — это норма); после reconnect догрузить пропуски через REST при необходимости. При **401** на HTTP после refresh — пересоздать WS с новым access (если токен в query — синхронизировать).  
- Не логировать содержимое сообщений в production.

## 10. Перехват 404

- В роутере последний маршрут — `ErrorNotFound.vue`.  
- Опционально `router.afterEach` для `document.title` и аналитики.

## 11. TypeScript

- Строгий режим в `tsconfig.json`.  
- Типы DTO рядом с API или из сгенерированного OpenAPI (на будущее).  
- `defineProps` / `defineEmits` с типами; composables возвращают явный интерфейс.

## 12. ESLint: популярный и поддерживаемый конфиг

Цель — единые правила для `.vue`, `.ts`, импортов и потенциальных багов Vue 3.

**Вариант A (часто удобнее всего для Vite + Vue + TS):** пакет **[`@antfu/eslint-config`](https://github.com/antfu/eslint-config)** — один пресет на базе **flat config** (`eslint.config.js`), уже включает TypeScript, Vue, форматирование/стиль по договорённостям Anthony Fu (широко используется в экосистеме Vue/Vite). Хорошо стыкуется с **Prettier** через `eslint-config-prettier`, если Prettier оставляете отдельной командой `format`.

**Вариант B (ближе к официальным рекомендациям Vue):** связка **`eslint-plugin-vue`** (правила `vue3-recommended`) + **`typescript-eslint`** (`@typescript-eslint/parser`, `@typescript-eslint/eslint-plugin`) + **`@eslint/js`**. Quasar CLI при генерации проекта часто подсказывает стартовый ESLint — можно **расширить** его этими пакетами, не ломая `quasar dev`.

**Практика:**

- в `package.json`: скрипты `"lint": "eslint ."` и `"lint:fix": "eslint . --fix"`;  
- в CI: `npm run lint` **до** `build` (как в [CI-CD.md](./CI-CD.md));  
- не отключать правила массово `eslint-disable` без причины.

Подробнее про запуск тестов фронта — [TESTING.md](./TESTING.md).

## 13. Тестирование фронта

Кратко: **Vitest** + **Vue Test Utils**; мок API через **MSW**; E2E позже. Полная матрица и приоритеты — в [TESTING.md](./TESTING.md).
