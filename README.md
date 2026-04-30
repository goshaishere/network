# Network

`Network` - социальная и рабочая платформа: профиль и стены, сообщества, личные сообщения, лента друзей, рабочие группы с канбан-досками, роли сотрудника (штат/партнер), админ-консоль и контур наблюдаемости.

## Что внутри продукта

- Социальный контур: профиль, стена, сообщества, друзья, персональная лента, вложения в постах, жалобы на контент.
- Коммуникации: личные диалоги (REST + WebSocket).
- Рабочий контур: `work`-группы, доски, колонки, задачи, CRM-заготовки.
- Доступ и роли: JWT auth, hCaptcha при рисковом логине, staff/admin, employee/internal/partner.
- Эксплуатация: Docker Compose для dev/stack, CI/CD в GitHub Actions, health/metrics/observability.

## Технологический стек

- Backend: `Python 3.13`, `Django 6`, `Django REST Framework`, `Channels`, `SimpleJWT`.
- Data: `PostgreSQL 18`, `Redis 7`.
- Frontend: `Vue 3`, `Quasar 2`, `Vite`, `TypeScript`.
- Infra: `Docker`, `Docker Compose`, `Nginx`, `GitHub Actions`, `GHCR`.
- Monitoring: Prometheus/Alertmanager/Grafana (опциональный overlay), Sentry.

## Структура репозитория

- `backend/` - API, бизнес-логика, миграции, тесты.
- `frontend/` - SPA на Quasar/Vue.
- `docs/` - архитектура, API, тестирование, CI/CD, пайплайн фаз.
- `infra/` - observability и служебные скрипты.
- `.github/workflows/` - CI и deploy workflow.

## Быстрый старт (локально)

### Вариант A: всё в Docker (рекомендуется)

1. Подготовьте env-файл:
   - скопируйте `.env.example` в `.env` (если отсутствует),
   - при необходимости поправьте переменные.
2. Поднимите сервисы:
   - `docker compose up --build`
3. Проверьте доступность:
   - API health: `http://127.0.0.1:8000/api/v1/health/`
   - фронт: `http://127.0.0.1:9000`

### Вариант B: backend/frontend раздельно

Backend:

1. `cd backend`
2. `python -m venv .venv`
3. Активируйте venv и установите зависимости: `pip install -r requirements.txt`
4. Для быстрого старта можно SQLite: `USE_SQLITE=1`
5. Миграции: `python manage.py migrate`
6. Запуск ASGI: `daphne -b 127.0.0.1 -p 8000 config.asgi:application`

Frontend:

1. `cd frontend`
2. `npm ci`
3. `npm run dev`

## Тесты и проверка качества

Backend:

- `cd backend && pytest`

Frontend:

- `cd frontend && npm run lint && npm run typecheck && npm run test && npm run build`

Основной CI-пайплайн: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

Что проверяется в CI:

- линт/формат backend;
- backend тесты (PostgreSQL service);
- frontend lint/typecheck/test/build;
- `docker compose config` для dev/stack/observability;
- сборка backend/frontend Docker images (без push) на PR;
- push образов в GHCR на `main`;
- `gitleaks` scan на потенциальные секреты.

## Контейнеры и образы

- `backend/Dockerfile` - multi-stage (builder/runtime), non-root runtime.
- `frontend/Dockerfile` - multi-stage (Vite build + nginx runtime).
- `docker-compose.yml` - локальная разработка.
- `docker-compose.stack.yml` - stage/prod deployment из registry-образов.
- `docker-compose.observability.yml` - overlay для Prometheus/Alertmanager/Grafana.

## Деплой (stage/prod)

### 1) Подготовка окружения сервера

1. На сервере создайте каталог проекта (например `/opt/network`).
2. Положите туда `docker-compose.stack.yml`.
3. Скопируйте `stack.env.example` в `.env` и заполните значения:
   - `NETWORK_BACKEND_IMAGE`, `NETWORK_FRONTEND_IMAGE`,
   - `SECRET_KEY`, `POSTGRES_PASSWORD`, домены и CORS.

Пример: [stack.env.example](stack.env.example)

### 2) Ручной запуск stack

- `docker compose -f docker-compose.stack.yml --env-file .env up -d`

В stack-режиме backend стартует с миграциями:

- `python manage.py migrate --noinput && daphne ...`

Smoke-check:

- `curl -fsS http://127.0.0.1/api/v1/health/ready/`

### 3) Деплой через GitHub Actions

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

Требуемые GitHub Secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`

Параметры запуска workflow:

- `environment`: `stage` или `production`
- `image_tag`: `sha-<commit_sha>` или `latest`

Логика deploy:

- подтягиваются образы из GHCR;
- выполняется `docker compose up -d`;
- выполняется smoke-check `health/ready`;
- при ошибке автоматически выполняется rollback к предыдущим image tags.

## Наблюдаемость

- Базовые health endpoints доступны через API.
- Метрики: `/api/v1/metrics/` (токен/доступ по настройке).
- Для полного контура подключайте `docker-compose.observability.yml`.
- Конфиги и примеры: `infra/observability/`.

## Полезные ссылки

- Общая документация: [`docs/README.md`](docs/README.md)
- Статус реализации фаз: [`docs/IMPLEMENTATION-STATUS.md`](docs/IMPLEMENTATION-STATUS.md)
- Backend API и домены: [`docs/BACKEND.md`](docs/BACKEND.md)
- Docker и эксплуатация: [`docs/DOCKER-DEPLOYMENT.md`](docs/DOCKER-DEPLOYMENT.md)
- CI/CD: [`docs/CI-CD.md`](docs/CI-CD.md)
- Тестирование: [`docs/TESTING.md`](docs/TESTING.md)
