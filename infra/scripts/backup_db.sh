#!/usr/bin/env sh
set -eu

: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=network}"
: "${POSTGRES_USER:=network}"
: "${POSTGRES_PASSWORD:=network}"

export PGPASSWORD="$POSTGRES_PASSWORD"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${1:-./backups/network_${STAMP}.sql.gz}"

mkdir -p "$(dirname "$OUT")"
pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$OUT"
echo "Backup created: $OUT"
