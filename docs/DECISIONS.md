# Зафиксированные решения (обновляется по мере обсуждения)

| Тема | Решение | Подробности |
|------|---------|-------------|
| Аутентификация API | **JWT** | `djangorestframework-simplejwt`: access + refresh, blacklist при logout (по желанию). Заголовок `Authorization: Bearer <access>`. |
| Капча | **hCaptcha** | Зафиксировано. Явный challenge после N неудачных логинов. См. [BACKEND.md](./BACKEND.md). |
| «Почта» в dev | **Mailhog в `docker-compose`** | Зафиксировано: SMTP в dev указывает на сервис `mailhog` (UI для писем сброса пароля). Не для ЛС. См. [EMAIL-VS-MESSAGING.md](./EMAIL-VS-MESSAGING.md). |
| ЛС в MVP | **WebSocket** | **Channels** + **Redis** (channel layer). REST для истории. Про рестарт процесса и WS — раздел **«2a»** в [ARCHITECTURE.md](./ARCHITECTURE.md). |
| Redis дополнительно | **По желанию** | Помимо channel layer: `CACHES`, throttling, опционально `SESSION_ENGINE` для Django (админка и т.д.). Не заменяет переподключение WS после рестарта процесса. |
| CI/CD хостинг | **GitHub Actions** (по умолчанию) | См. [CI-CD.md](./CI-CD.md); другой CI — перенос workflow. |
| Роли и продукт | **user / employee / admin** | **`user`** — соцконтур + **сообщества**, без **`/work/*`**. **`employee`**+ — рабочие группы, канбан, **`/work`**. **`admin`** — консоль. См. [ROLES-AND-TASKS.md](./ROLES-AND-TASKS.md). |
| Сообщества vs работа | **Раздельно** | **`Community`** — для всех **`user+`**. **`WorkGroup`** — только сотрудники. |
| Штат vs партнёр | **`EmploymentKind`** | `internal` — полный внутренний рабочий контур; `partner` — только выданные группы/доски, без **`/api/v1/internal/...`**. |
| Колонки канбана | **Единый перечень `semantic` + пресеты** | См. [ROLES-AND-TASKS.md](./ROLES-AND-TASKS.md) §6. |
| Мониторинг (ориентир) | **Sentry + Prometheus/Grafana**; Zabbix по необходимости | См. [MONITORING-AND-SUPPORT.md](./MONITORING-AND-SUPPORT.md). «Пирамида» в обсуждении чаще = **Prometheus**. |
| Свой почтовый сервер | **Не в MVP**; экстра-фаза | См. [SELF-HOSTED-MAIL.md](./SELF-HOSTED-MAIL.md); в MVP — внешний SMTP или Mailhog в dev. |
| Линтер фронта | **ESLint** | Пресет `@antfu/eslint-config` **или** `eslint-plugin-vue` + `typescript-eslint` (см. [FRONTEND.md](./FRONTEND.md) §12). |
| Тесты | **Обязательны для бэка и фронта** | `pytest` / `pytest-django`; **Vitest** + Vue Test Utils; всё в CI. См. [TESTING.md](./TESTING.md). |
| Главная vs дашборд | **Раздельно** | **`/`** — лёгкая соцточка; **`/dashboard`** — настраиваемые виджеты + pin; **`/work`** — рабочий хаб. См. [ROLES-AND-TASKS.md](./ROLES-AND-TASKS.md) §5. |

### Почему не reCAPTCHA v3 как основная для входа

v3 даёт **оценку 0–1** без явной галочки: удобно для фоновой антибот-оценки, но для сценария «с 3-й ошибки **обязательно** докажи, что человек» надёжнее **виджет с явным challenge** — **hCaptcha** или reCAPTCHA **v2 checkbox**. v3 можно добавить позже как дополнительный сигнал.
