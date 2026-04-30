# Наблюдаемость и алерты (фаза 6)

## Эндпоинты

| Путь | Назначение |
|------|------------|
| `GET /api/v1/health/` | БД, Redis (если используется Channels Redis), диск, `APP_VERSION`. 503 при критичных сбоях. |
| `GET /api/v1/health/live/` | Liveness: процесс отвечает (всегда 200). |
| `GET /api/v1/health/ready/` | Readiness: БД + Redis при необходимости + диск не critical. Используется в Docker healthcheck и после деплоя. |
| `GET /api/v1/metrics/` | Prometheus: staff **или** `METRICS_SCRAPE_TOKEN` в заголовке `X-Metrics-Token` / query `?token=`. |

Внешний **uptime** (UptimeRobot, healthchecks.io): проверяйте `GET /api/v1/health/` или `.../health/ready/` по публичному URL API.

## Локальный стек Prometheus + Grafana

1. Скопируйте [`infra/observability/bearer.token.example`](../../infra/observability/bearer.token.example) в `infra/observability/bearer.token` и задайте длинный токен.
2. В `.env` для `api` добавьте `METRICS_SCRAPE_TOKEN=<тот же токен>`.
3. Запуск:  
   `docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up -d`  
4. Prometheus: http://localhost:9090 — правила в [`infra/observability/alerts.yml`](../../infra/observability/alerts.yml).  
5. Alertmanager: http://localhost:9093 — настройте `receivers` в [`infra/observability/alertmanager.yml`](../../infra/observability/alertmanager.yml).  
6. Grafana: http://localhost:3000 — добавьте datasource Prometheus (`http://prometheus:9090`).

## Production

- `SENTRY_DSN` — ошибки и стектрейсы ([`config/settings/production.py`](../../backend/config/settings/production.py)).  
- Логи: `LOG_LEVEL`, формат в stdout ([`production.py`](../../backend/config/settings/production.py)).  
- Секрет scrape: храните `METRICS_SCRAPE_TOKEN` только в env/secrets, не в Git.
