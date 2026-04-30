# Мониторинг, поддержка и сопровождение

Речь про **наблюдаемость** приложения (здоровье API, ошибки, метрики) и процесс реагирования. Если в обсуждении звучало «**Пирамида**» — чаще всего имеют в виду стек **Prometheus** (имя по-русски произносят похоже). **Zabbix** — отдельный, более «классический» мониторинг инфраструктуры.

## 1. Zabbix vs Prometheus (и «что ещё»)

| Инструмент | Сильные стороны | Типичное применение для Network |
|------------|-----------------|----------------------------------|
| **Zabbix** | Агенты, SNMP, шаблоны хостов, **инфраструктура** (CPU, диск, сеть), алерты из коробки | VPS/железо, PostgreSQL, Redis, Nginx — «жив ли сервер», место на диске |
| **Prometheus + Grafana** | **Метрики приложения** (histogram, RPS, latency), гибкие дашборды, PromQL | Микросервисы и монолит с `/metrics`: запросы к API, пул БД, длительность задач |
| **Sentry** (или аналог) | **Ошибки и стектрейсы** фронта и бэка, релизы, breadcrumbs | Исключения Django, Vue errors — первое, что подключают для «поддержки» |

**Практичная связка для проекта вашего класса:**

1. **Sentry** (или GlitchTip self-hosted) — ошибки и группировка инцидентов.  
2. **Prometheus + Grafana** (или облачный Grafana Cloud / Datadog по бюджету) — метрики приложения и инфраструктуры Kubernetes/VPS.  
3. **Zabbix** — **опционально**, если уже есть команда на Zabbix или нужен единый «классический» мониторинг хостов без Kubernetes.

Итого: **не «или-или»** — **Sentry + Prometheus/Grafana** закрывают большинство задач разработки и эксплуатации; **Zabbix** добавляют, если так принято в организации.

## 2. Минимум без тяжёлого стека

- **Healthcheck:** `GET /api/v1/health/` — БД, Redis (если Channels на Redis), диск, `APP_VERSION`; **`/api/v1/health/live/`** (liveness), **`/api/v1/health/ready/`** (readiness для Docker/K8s).  
- **Метрики:** `GET /api/v1/metrics/` (Prometheus) — staff или токен `METRICS_SCRAPE_TOKEN`; опционально compose **Prometheus + Alertmanager + Grafana**: см. [`docker-compose.observability.yml`](../docker-compose.observability.yml), [runbooks/observability.md](./runbooks/observability.md).  
- **Логи:** в production — `LOG_LEVEL`, вывод в stdout ([`production.py`](../backend/config/settings/production.py)) → **Loki**, **ELK** и т.д.  
- **Sentry:** `SENTRY_DSN` в production.  
- **Аптайм:** внешний ping (UptimeRobot, Better Stack, healthchecks.io) на `/api/v1/health/` или `/health/ready/`.

## 3. Метрики приложения (Prometheus)

- Экспорт через **`django-prometheus`** или OpenTelemetry → OTLP.  
- Интересные метрики: RPS, 5xx rate, latency p95, размер очереди Celery (если появится), WS-подключения (gauge).

## 4. Поддержка (процесс)

- Канал инцидентов (Telegram/Slack/on-call).  
- Связка **Sentry** → задача в **вашем таск-трекере** (канбан) для сотрудников.  
- Runbook в `docs/runbooks/` (как откатить релиз, как поднять БД из бэкапа).

## 5. Пайплайн

Внедрение мониторинга заложено в [PROJECT-PIPELINE.md](./PROJECT-PIPELINE.md) (фаза после стабилизации продакшена). Конкретные Helm-chart’ы или compose-файлы для Prometheus — появятся при реализации инфраструктуры.
