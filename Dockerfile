# ==========================================================
# ConciliaAI – Dockerfile ("Docker único" • app image)
# ----------------------------------------------------------
# Builds ONE application image containing:
#   - the React frontend (static build), and
#   - the FastAPI backend, which also serves the static build.
#
# PostgreSQL is intentionally NOT part of this image. For a financial
# system the database must remain an EXTERNAL service (durability,
# backup, restore, independent scaling) — see docker-compose.yml.
#
# Startup applies Alembic migrations and runs the idempotent seed.
# Failures are NOT masked with "|| true": if migrations fail the
# container fails fast instead of starting against a broken schema.
# ==========================================================

# ---------- STAGE 1: FRONTEND BUILD ----------
FROM node:20-slim AS frontend-builder
WORKDIR /frontend

# Install dependencies first for better layer caching.
COPY conciliaai-frontend/package.json conciliaai-frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

# Build the SPA. Same-origin API calls (empty base URL) because the
# backend serves these assets from the same container/host.
COPY conciliaai-frontend/ ./
ENV VITE_API_BASE_URL=""
RUN npm run build

# ---------- STAGE 2: PYTHON BUILDER ----------
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --user -r requirements.txt \
 && pip check

# ---------- STAGE 3: RUNTIME ----------
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
WORKDIR /app

# Python dependencies from the builder stage.
COPY --from=builder /root/.local /home/appuser/.local

# Backend source (selective copy = fast builds).
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./alembic.ini

# Frontend static build, served by FastAPI (see src/api/main.py).
COPY --from=frontend-builder --chown=appuser:appuser /frontend/dist ./static

USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    FRONTEND_DIST=/app/static \
    LOG_LEVEL=INFO

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

# ---------- CMD AUTO-INIT ----------
# `set -e` ensures a failing migration aborts startup (no masking).
# The seed is idempotent and treated as best-effort (it must not block
# startup if, e.g., demo data is intentionally absent), but migrations
# are mandatory.
CMD ["sh", "-c", "set -e; \
  echo '📦 Applying Alembic migrations...'; \
  alembic upgrade head; \
  echo '🌱 Seeding database (idempotent)...'; \
  python scripts/seed_database.py; \
  echo '🚀 Starting Uvicorn server...'; \
  exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
