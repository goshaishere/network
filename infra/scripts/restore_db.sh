#!/usr/bin/env sh
set -eu

if [ $# -lt 1 ]; then
  echo "Usage: $0 <backup.sql.gz>"
  exit 1
fi

FILE="$1"
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=network}"
: "${POSTGRES_USER:=network}"
: "${POSTGRES_PASSWORD:=network}"

export PGPASSWORD="$POSTGRES_PASSWORD"
gunzip -c "$FILE" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
echo "Restore completed from: $FILE"
