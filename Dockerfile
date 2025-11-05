# ==========================================================
# ConciliaAI – Dockerfile (BuildToValue v7.1 • Auto-Init Mode)
# ----------------------------------------------------------
# Features:
#  - Multi-stage (builder/runtime) p/ imagem leve
#  - COPY seletivo + .dockerignore
#  - Alembic upgrade + seed no startup (idempotente)
#  - Usuário não-root (appuser)
# ==========================================================

# ---------- STAGE 1: BUILDER ----------
FROM python:3.11-slim AS builder
WORKDIR /app

# Dependências de build (temporárias)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Cache de deps Python
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --user -r requirements.txt \
 && pip check

# ---------- STAGE 2: RUNTIME ----------
FROM python:3.11-slim

# Somente libs de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

# Usuário de app
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Deps Python do builder
COPY --from=builder /root/.local /home/appuser/.local

# Código (cópia seletiva = build rápido)
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./alembic.ini

# Ambiente
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

# ---------- CMD AUTO-INIT ----------
CMD ["sh","-c","set -e; \
  echo '📦 Applying Alembic migrations...'; \
  alembic upgrade head || echo '⚠️ Alembic: sem mudanças/aviso.'; \
  echo '🌱 Seeding database (if needed)...'; \
  python scripts/seed_database.py || echo '⚠️ Seed: ignorado/sem mudanças.'; \
  echo '🚀 Starting Uvicorn server...'; \
  exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
