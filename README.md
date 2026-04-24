# Network

Платформа **Network**: **сообщества** и соцпрофиль для всех; лёгкая главная **`/`**, настраиваемый **`/dashboard`** (виджеты, закрепление); **рабочий контур** **`/work`** для сотрудников (**штат / партнёр**); **админ-панель**; **WebSocket**, **JWT**, hCaptcha, Docker.

**Стек:** Django 6 · DRF · PostgreSQL 18 · Quasar 2 · Vue 3 · Vite · TypeScript · Docker.

Документация по архитектуре, датафлоу, БД, Docker и CI/CD — в каталоге **[docs/](docs/README.md)**.

## Быстрый старт (фаза 1)

- **Всё в Docker:** из корня `docker compose up --build`, API: `http://127.0.0.1:8000/api/v1/health/`.
- **Бэкенд локально (SQLite):** в `backend/` задать `USE_SQLITE=1`, выполнить `python manage.py migrate`, затем `daphne -b 127.0.0.1 -p 8000 config.asgi:application`.
- **Фронт:** в `frontend/` — `npm install`, `npm run dev` (порт **9000**, прокси `/api` → 8000).

Пример переменных: **[.env.example](.env.example)**. CI: **[.github/workflows/ci.yml](.github/workflows/ci.yml)**.
