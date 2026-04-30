FROM python:3.13-slim-bookworm AS builder

WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
