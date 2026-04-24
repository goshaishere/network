# Network — документация

Социальная сеть (ВК-функционал) **и** рабочий контур: роли **пользователь / сотрудник / админ**, таск-трекер с **канбаном**, админ-панель (по мере развития).

**Стек (целевой):** Django 6 · Django REST Framework · PostgreSQL 18 · Quasar 2 · Vue 3 · Vite · TypeScript · Docker.

| Документ | Содержание |
|----------|------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | От общего к частному: репозиторий, слои, домены, классы и ответственность |
| [DATAFLOW.md](./DATAFLOW.md) | Датафлоу по сущностям: auth, профиль, стена, ЛС, ошибки |
| [BACKEND.md](./BACKEND.md) | Django-приложения, DRF, **JWT**, WebSocket/Channels, эндпоинты |
| [FRONTEND.md](./FRONTEND.md) | Quasar, лейауты, SCSS, i18n, темы, страницы, composables |
| [DATABASE.md](./DATABASE.md) | PostgreSQL, папка `database/`, миграции, что коммитить |
| [DOCKER-DEPLOYMENT.md](./DOCKER-DEPLOYMENT.md) | Compose, переменные окружения, запуск и развёртывание |
| [CI-CD.md](./CI-CD.md) | Пайплайны CI/CD, проверки, артефакты |
| [TESTING.md](./TESTING.md) | Тесты **бэкенда и фронта**, инструменты, CI |
| [PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md) | Фазы проекта от архитектуры до релизов |
| [IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md) | **Статус реализации кода** относительно фаз пайплайна (обновлять вместе с PR) |
| [DECISIONS.md](./DECISIONS.md) | Зафиксированные решения: JWT, капча, WS, dev-почта |
| [EMAIL-VS-MESSAGING.md](./EMAIL-VS-MESSAGING.md) | Транзакционная почта (SMTP) ≠ ЛС; Mailhog; «перехват» трафика |
| [ROLES-AND-TASKS.md](./ROLES-AND-TASKS.md) | Сообщества / работа, штат/партнёр, **`/`**, **`/dashboard`** (виджеты, pin), **`/work`**, статусы §7, админка |
| [MONITORING-AND-SUPPORT.md](./MONITORING-AND-SUPPORT.md) | Мониторинг: Prometheus/Grafana, Zabbix, Sentry, поддержка |
| [SELF-HOSTED-MAIL.md](./SELF-HOSTED-MAIL.md) | Свой почтовый сервер как **экстра** в пайплайне |

Пайплайн реализации и порядок фаз — **[PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md)** (включая сводку по **статусам задач** и блок **«Окончательный порядок при старте кода»**). Актуальное соответствие коду — **[IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md)**. Дальше — реализация: `backend/`, `frontend/`, `docker-compose.yml`.
