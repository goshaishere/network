# Docker: запуск, развёртывание, окружения

## 1. Цели

- Один **`docker compose up`** для локальной разработки: API (**ASGI**) + Postgres + **Redis** + **Mailhog** (SMTP в dev; зафиксировано) + фронт по желанию в контейнере или на хосте.  
- Образы, пригодные для **CI** (тесты бэка) и **CD** (push в registry, деплой на сервер/k8s).

## 2. Сервисы (рекомендуемый состав)

| Сервис | Образ / сборка | Порт (dev) | Назначение |
|--------|-----------------|------------|------------|
| `db` | `postgres:18` (или `-alpine`) | 5432 внутри сети compose | Данные |
| `api` | Dockerfile из `backend/` | 8000 | **Daphne/Uvicorn** + Django (**ASGI**, REST + WS) |
| `web` | Dockerfile из `frontend/` (multi-stage: build → nginx) | 80/443 | Статика SPA |
| `proxy` | Nginx/Caddy (опционально) | 80 | Единая точка входа |
| `redis` | `redis:7-alpine` | 6379 | **Channels channel layer** (обязательно для WS); плюс throttling/кэш |
| `mailhog` | `mailhog/mailhog` | 8025 UI, 1025 SMTP | **Обязательный** сервис в dev-compose: перехват **SMTP** (сброс пароля), не ЛС |

На чистом dev часто запускают **Quasar на хосте** (`quasar dev`), а в Docker — `db`, `redis`, `mailhog`, `api` — так HMR быстрее, почта и WS всё равно работают.

### 2a. Redis и рестарт API

Redis **не** сохраняет активное WebSocket-соединение при перезапуске процесса API; он нужен для **Channels channel layer** (и опционально кэш/лимиты). После рестарта клиент **переподключается** к WS; данные ЛС — в Postgres. Подробнее: [ARCHITECTURE.md](./ARCHITECTURE.md) раздел **«2a»**.

## 3. Переменные окружения (пример набора)

**Backend (`api`):**

- `DJANGO_SETTINGS_MODULE=config.settings.local`  
- `SECRET_KEY` — только из секретов, не в Git  
- `DEBUG=0` в production  
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`  
- `DATABASE_URL` или набор `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`  
- `CORS_ALLOWED_ORIGINS` — URL фронта  
- `HCAPTCHA_SECRET_KEY` (сервер), sitekey на фронте: `VITE_HCAPTCHA_SITEKEY`  
- `EMAIL_*` / `DJANGO_EMAIL_*`: для **транзакционной почты** (сброс пароля). В dev указать SMTP на сервис **Mailhog** (`MAILHOG` host `mailhog`, порт `1025`). Подробнее: [EMAIL-VS-MESSAGING.md](./EMAIL-VS-MESSAGING.md).

**Frontend (build-time `VITE_*`):**

- `VITE_API_URL=https://api.example.com/api/v1`  
- `VITE_WS_URL=wss://api.example.com` (или отдельный ws-хост)  
- `VITE_HCAPTCHA_SITEKEY=...`

## 4. Volumes и папка `database/`

- Том данных Postgres: см. [DATABASE.md](./DATABASE.md).  
- Пример: `./database/pgdata:/var/lib/postgresql/data` + `.gitignore` на `database/pgdata/`.

## 5. Dockerfile backend (логика)

- Базовый образ `python:3.12-slim` (или версия, совместимая с Django 6).  
- Установка зависимостей из `requirements.txt` / `uv.lock`.  
- `collectstatic` на этапе CI/CD или в entrypoint для production.  
- Команда: `daphne -b 0.0.0.0 -p 8000 config.asgi:application` (или `uvicorn config.asgi:application --host 0.0.0.0 --port 8000`).

## 6. Dockerfile frontend (логика)

- Stage 1: `node:22-alpine`, `npm ci`, `quasar build` (или `pnpm`).  
- Stage 2: `nginx:alpine` — копия `dist/spa` (путь зависит от режима Quasar), `try_files` для SPA fallback на `index.html`.  
- Отдельно: проксирование `/api` на сервис `api` **только если** один origin; иначе CORS с отдельного API-домена.

## 7. Локальный запуск (инструкция после появления кода)

1. Склонировать репозиторий, скопировать env:  
   `cp .env.example .env` и заполнить секреты.  
2. `docker compose build`  
3. `docker compose up -d db redis mailhog` → дождаться healthy.  
4. `docker compose run --rm api python manage.py migrate`  
5. `docker compose run --rm api python manage.py createsuperuser` (опционально)  
6. `docker compose up api web` (или только `api`, фронт на хосте)  
7. Открыть фронт по порту из compose (например `http://localhost:9000` или через proxy `http://localhost`).

Точные команды зафиксировать в корневом `README.md` после реализации.

## 8. Production

- **Секреты** — Docker secrets, Vault, или переменные платформы (Fly.io, Railway, K8s Secrets).  
- **Миграции** — job перед выкаткой новой версии API (`migrate`).  
- **Статика** — WhiteNoise или S3+CloudFront; медиа — object storage.  
- **TLS** — на edge (Cloudflare, ALB, Caddy).  
- **Бэкапы** — автоматические снимки БД по расписанию, проверка восстановления.

## 9. Файлы в репозитории

- `docker-compose.yml` — базовый dev.  
- `docker-compose.prod.yml` — overrides без проброса исходников, с лимитами ресурсов.  
- `.dockerignore` в `backend/` и `frontend/` — исключить `node_modules`, `.git`, `__pycache__`.
