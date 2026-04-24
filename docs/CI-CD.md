# CI/CD: пайплайны и автоматизация

Предполагается **GitHub Actions** (аналогично переносится на GitLab CI / Gitea).

## 1. Цели пайплайна

- Быстрая обратная связь на каждый PR.  
- Запрет merge при падающих проверках (branch protection).  
- Сборка артефактов (образы Docker) на `main` / теги для деплоя.

## 2. Jobs (рекомендуемый набор)

### 2.1 `backend-lint`

- Инструменты: `ruff check`, `ruff format --check` (или black + isort — выбрать один стиль).  
- Рабочая директория: `backend/`.

### 2.2 `backend-test`

- Сервис-контейнер `postgres:18` в workflow с healthcheck.  
- Переменные: `DATABASE_URL`, `SECRET_KEY` тестовый.  
- Команды: `pip install -r requirements.txt`, `pytest` / `python manage.py test`.  
- Кэш pip по хэшу lock-файла.

### 2.3 `frontend-lint-typecheck`

- `npm ci` в `frontend/`.  
- `npm run lint` — **ESLint** (конфиг см. [FRONTEND.md](./FRONTEND.md), §12: `@antfu/eslint-config` или `eslint-plugin-vue` + `typescript-eslint`).  
- `npm run typecheck` или `vue-tsc --noEmit`.

### 2.4 `frontend-test`

- После установки зависимостей: **`vitest run`** (или `npm run test` — зафиксировать в `package.json`).  
- Тот же job может кэшировать `node_modules` по lock-файлу.  
- Подробности стратегии: [TESTING.md](./TESTING.md).

### 2.5 `frontend-build`

- `npm run build` — production-сборка после успешных lint/typecheck/**test**.

### 2.6 `docker-build` (на `main` и tags)

- `docker buildx build` для `backend` и `frontend` с push в GHCR (или ECR/GCR).  
- Теги: `sha-${GITHUB_SHA}`, `main`, семвер с git tag.

### 2.7 `deploy` (опционально, по кнопке или на tag)

- Триггер: `workflow_dispatch` или `push` на `v*`.  
- Шаги: обновить манифест k8s / вызвать API PaaS / SSH + `docker compose pull` — зависит от хостинга.

## 3. Пример структуры workflow (псевдокод)

Файл: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_USER: network
          POSTGRES_PASSWORD: network
          POSTGRES_DB: network_test
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
        working-directory: backend
      - run: pytest
        working-directory: backend
        env:
          DATABASE_URL: postgres://network:network@localhost:5432/network_test

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci && npm run lint && npm run typecheck && npm run test && npm run build
        working-directory: frontend
```

Скрипты `typecheck` и `test` (`vitest run`) добавить в `frontend/package.json` при инициализации Quasar-проекта; до появления тестов можно временно использовать `vitest run --passWithNoTests` или отдельный job `frontend-test`, не блокирующий merge, пока не накопится база тестов — лучше сразу включить **хотя бы один smoke-тест**, чтобы пайплайн не «усыхал». Стратегия покрытий: [TESTING.md](./TESTING.md).

После появления реальных `package.json` / `requirements.txt` пути и скрипты уточняются.

## 4. Секреты CI

В GitHub **Settings → Secrets**:

- `REGISTRY_TOKEN`, `KUBE_CONFIG`, `SSH_KEY`, `PRODUCTION_ENV` — по необходимости.  
- Никогда не печатать секреты в логах.

## 5. Качество релиза

- Автоматический **changelog** из Conventional Commits (опционально).  
- **Semantic versioning** для API при ломающих изменениях (`/api/v2/`).

## 6. Связь с пайплайном проекта

Этапы планирования и сдачи фич — в [PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md).

## 7. Текущая реализация в репозитории

- CI: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — backend lint/test, frontend lint/typecheck/test/build, docker build+push в GHCR на `main`.
- CD: [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) — ручной deploy по `workflow_dispatch` (SSH), `docker compose up`, миграции и health-check.
- Контейнеры: [`backend/Dockerfile`](../backend/Dockerfile), [`frontend/Dockerfile`](../frontend/Dockerfile), [`docker-compose.yml`](../docker-compose.yml).
- Бэкапы БД: [`infra/scripts/backup_db.sh`](../infra/scripts/backup_db.sh), [`infra/scripts/restore_db.sh`](../infra/scripts/restore_db.sh).
