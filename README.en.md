# Network

`Network` is a social + work platform: profile and walls, communities, direct messages, friends feed, employee workgroups with kanban boards, admin console, and observability tooling.

## Product Overview

- Social features: profile, wall, communities, friends, personal feed, post attachments, content reports.
- Messaging: direct conversations (REST + WebSocket).
- Work domain: `work` groups, boards, columns, tasks, CRM stubs.
- Access model: JWT auth, hCaptcha on risky login flow, staff/admin, employee/internal/partner scopes.
- Operations: Docker Compose for dev/stack, GitHub Actions CI/CD, health/metrics/observability.

## Tech Stack

- Backend: `Python 3.13`, `Django 6`, `Django REST Framework`, `Channels`, `SimpleJWT`.
- Data: `PostgreSQL 18`, `Redis 7`.
- Frontend: `Vue 3`, `Quasar 2`, `Vite`, `TypeScript`.
- Infra: `Docker`, `Docker Compose`, `Nginx`, `GitHub Actions`, `GHCR`.
- Monitoring: Prometheus/Alertmanager/Grafana (optional overlay), Sentry.

## Repository Structure

- `backend/` - API, business logic, migrations, tests.
- `frontend/` - Quasar/Vue SPA.
- `docs/` - architecture, API, testing, CI/CD, project pipeline docs.
- `infra/` - observability and support scripts.
- `.github/workflows/` - CI and deployment workflows.

## Local Run

### Option A: Full Docker setup (recommended)

1. Prepare env file:
   - copy `.env.example` to `.env` (if needed),
   - adjust values for your machine.
2. Start services:
   - `docker compose up --build`
3. Verify:
   - API health: `http://127.0.0.1:8000/api/v1/health/`
   - frontend: `http://127.0.0.1:9000`

### Option B: Backend and frontend separately

Backend:

1. `cd backend`
2. `python -m venv .venv`
3. Activate venv and install deps: `pip install -r requirements.txt`
4. For quick local run you can use SQLite: `USE_SQLITE=1`
5. Run migrations: `python manage.py migrate`
6. Start ASGI app: `daphne -b 127.0.0.1 -p 8000 config.asgi:application`

Frontend:

1. `cd frontend`
2. `npm ci`
3. `npm run dev`

## Testing and Quality

Backend:

- `cd backend && pytest`

Frontend:

- `cd frontend && npm run lint && npm run typecheck && npm run test && npm run build`

Main CI workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

CI includes:

- backend lint/format checks;
- backend tests (with PostgreSQL service);
- frontend lint/typecheck/test/build;
- `docker compose config` validation for dev/stack/observability;
- Docker image build verification on PRs (no push);
- image publish to GHCR on `main`;
- `gitleaks` secrets scanning.

## Containers and Images

- `backend/Dockerfile` - multi-stage (builder/runtime), non-root runtime.
- `frontend/Dockerfile` - multi-stage (Vite build + nginx runtime).
- `docker-compose.yml` - local development.
- `docker-compose.stack.yml` - stage/prod deployment from registry images.
- `docker-compose.observability.yml` - Prometheus/Alertmanager/Grafana overlay.

## Deployment (Stage/Prod)

### 1) Prepare server environment

1. Create project directory on server (for example `/opt/network`).
2. Put `docker-compose.stack.yml` there.
3. Copy `stack.env.example` to `.env` and fill values:
   - `NETWORK_BACKEND_IMAGE`, `NETWORK_FRONTEND_IMAGE`,
   - `SECRET_KEY`, `POSTGRES_PASSWORD`, host/CORS values.

Reference file: [stack.env.example](stack.env.example)

### 2) Manual stack run

- `docker compose -f docker-compose.stack.yml --env-file .env up -d`

In stack mode backend starts with migrations:

- `python manage.py migrate --noinput && daphne ...`

Smoke check:

- `curl -fsS http://127.0.0.1/api/v1/health/ready/`

### 3) Deploy via GitHub Actions

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

Required GitHub Secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`

Workflow inputs:

- `environment`: `stage` or `production`
- `image_tag`: `sha-<commit_sha>` or `latest`

Deploy flow:

- pulls target images from GHCR;
- runs `docker compose up -d`;
- runs readiness smoke-check;
- on failure, auto-rolls back to previous image tags.

## Observability

- Base health endpoints are exposed by API.
- Metrics endpoint: `/api/v1/metrics/` (token/role-protected by settings).
- For full monitoring stack, use `docker-compose.observability.yml`.
- Configs and examples: `infra/observability/`.

## Useful Links

- Docs index: [`docs/README.md`](docs/README.md)
- Implementation status by phases: [`docs/IMPLEMENTATION-STATUS.md`](docs/IMPLEMENTATION-STATUS.md)
- Backend/API details: [`docs/BACKEND.md`](docs/BACKEND.md)
- Docker and operations: [`docs/DOCKER-DEPLOYMENT.md`](docs/DOCKER-DEPLOYMENT.md)
- CI/CD details: [`docs/CI-CD.md`](docs/CI-CD.md)
- Testing guide: [`docs/TESTING.md`](docs/TESTING.md)
