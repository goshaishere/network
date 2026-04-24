# База данных: PostgreSQL и папка `database/`

## Можно ли хранить данные PostgreSQL в папке `database` внутри проекта?

**Кратко:** да для **локальной разработки в Docker**, если это **том (volume)** с файлами кластера — но эту папку **нельзя коммитить в Git** (только в `.gitignore`).

### Два разных смысла «database»

1. **Данные кластера PostgreSQL** (бинарные файлы БД: `PGDATA`)  
   - Удобно смонтировать как `./database/pgdata` или использовать **именованный Docker volume** (`network_pgdata`).  
   - В репозитории держите **пустую** игнорируемую директорию или только placeholder, не сами файлы БД.  
   - На **production** обычно: managed PostgreSQL (RDS, Cloud SQL, Azure, etc.) или отдельный сервер/кластер, не папка в репозитории.

2. **Артефакты разработки** (разрешено в Git)  
   - `database/init/` — опциональные `*.sql` для локального сида (осторожно: не дублируйте то, что уже делает Django migrations).  
   - Документация схемы, диаграммы — в `docs/`.

### Рекомендуемая структура в монорепо

```
network/
  database/                 # опционально
    .gitkeep                # чтобы папка существовала в git
    README.md               # по желанию: что сюда монтируется
  # реальные pgdata — только через volume, в .gitignore:
  # database/pgdata/
```

В `docker-compose.yml` для dev:

```yaml
volumes:
  - ./database/pgdata:/var/lib/postgresql/data
```

И в `.gitignore`:

```
database/pgdata/
```

### Версия PostgreSQL

Целевая **PostgreSQL 18** в Docker-образе; версию клиента в CI согласовать с сервером (минимум совместимый major).

### Схема и миграции

- **Источник правды по схеме** — модели Django + `python manage.py makemigrations` / `migrate`.  
- Raw SQL в репозитории — только для редких операций (индексы вручную, extension `pg_trgm` и т.д.) и с описанием в `docs/` или в миграции через `RunSQL`.

### Расширения (по необходимости)

- `citext` — case-insensitive email/username (альтернатива: нормализация в приложении).  
- `pg_trgm` — поиск по тексту.  
- UUID primary keys — через `uuid` в Django или `gen_random_uuid()` в Postgres.
