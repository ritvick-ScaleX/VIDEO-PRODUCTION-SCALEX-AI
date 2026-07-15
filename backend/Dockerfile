# syntax=docker/dockerfile:1
# ============================================================================
# Auralis backend — FastAPI + Celery + Playwright
# Single image used by both the `backend` (api) and `worker` (celery) services.
# ============================================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# System deps: build tools for asyncpg/greenlet + Playwright/Chromium runtime libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
        libdrm2 libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 libxcomposite1 \
        libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
        libcairo2 libasound2 libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Chromium for the scraper. Non-fatal if it can't fetch (mock/offline builds).
RUN playwright install chromium || true

COPY . .

RUN mkdir -p /app/storage_data

EXPOSE 8000

# Bind Railway's injected $PORT (falls back to 8000 locally). Shell form so it expands.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
