# ===============================================
# BuildToValue v7.1 - ConciliaAI Full Automation
# ===============================================
.PHONY: help setup install start check-python fix-pip test test-cov test-integration test-accuracy test-performance test-load test-load-k6 test-stress test-all benchmark lint format run migrate migrate-create generate-migration seed docker-up docker-down docker-logs docker-reset init-db init-tenant fix-db reset-db

SHELL := cmd.exe
.SHELLFLAGS := /c "setlocal EnableDelayedExpansion &&"

# --------------------------------------
# 🔧 Environment Check & Setup
# --------------------------------------

help:
	@chcp 65001 >nul 2>&1
	@echo ConciliaAI - Available commands:
	@echo.
	@echo 🚀 Quick Start:
	@echo   make start        - Full environment setup (reset + migrate + tenant + healthcheck)
	@echo   make reset-db     - Clean all Docker data and rebuild from scratch
	@echo.
	@echo 🐘 Database:
	@echo   make migrate      - Apply Alembic migrations
	@echo   make init-tenant  - Ensure default tenant exists
	@echo.
	@echo 🐳 Docker:
	@echo   make docker-up    - Start containers
	@echo   make docker-down  - Stop containers
	@echo   make docker-logs  - Tail logs
	@echo.

check-python:
	@chcp 65001 >nul 2>&1
	@echo 🔍 Checking prerequisites...
	@where python >nul 2>&1 || (echo ❌ Python not found. Install Python 3.11+ && exit /b 1)
	@where docker >nul 2>&1 || (echo ❌ Docker not found. Install Docker Desktop && exit /b 1)
	@python --version | findstr /C:"3.11" >nul || python --version | findstr /C:"3.12" >nul || (echo ⚠️  WARNING: Python 3.11–3.12 recommended. && timeout /t 2 >nul)
	@echo ✅ Prerequisites OK

# --------------------------------------
# 🐳 Docker / DB Orchestration
# --------------------------------------

docker-up:
	@docker-compose up -d
	@echo ⏳ Waiting for services to be ready...
	@timeout /t 5 /nobreak >nul
	@docker-compose ps

docker-down:
	@docker-compose down -v

docker-logs:
	@docker-compose logs -f

docker-reset:
	@echo ♻️ Full docker reset...
	@docker-compose down -v
	@docker volume rm conciliaai_postgres_data --force || true
	@docker-compose up -d postgres
	@echo ⏳ Waiting for Postgres health...
	@timeout /t 25 /nobreak >nul
	@docker-compose run --rm backend alembic upgrade head
	@docker-compose up -d backend
	@echo ✅ Docker environment fully reset!

# --------------------------------------
# 🗄️ Database Commands
# --------------------------------------

migrate:
	@chcp 65001 >nul 2>&1
	@echo ⚙️ Regenerating and applying migrations...
	@docker-compose run --rm backend alembic revision --autogenerate -m "auto_full_schema" || echo ⚠️ Skipping generation...
	@docker-compose run --rm backend alembic upgrade head
	@echo ✅ Migrations applied successfully

# ✅ --- FIX 1: init-tenant with smart wait ---
init-tenant:
	@chcp 65001 >nul 2>&1
	@echo 🏗️ Ensuring default tenant exists \(ConciliaAI MVP\)...
	@echo ⏳ Waiting for 'tenants' table to be ready...
	@for /l %%i in (1,1,30) do ( \
		docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -tAc "SELECT 1 FROM pg_tables WHERE tablename='tenants';" | find "1" >nul && (echo ✅ Table ready! & goto table_ready) || (echo . waiting... & timeout /t 3 >nul) \
	) \
	& echo ❌ Timeout waiting for tenants table. Check migrations. & exit /b 1

	:table_ready
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "INSERT INTO tenants (id, org_name, cnpj, tier, active) VALUES (gen_random_uuid(), 'ConciliaAI MVP', '00000000000001', 'alpha', true) ON CONFLICT DO NOTHING;"
	@echo ✅ Default tenant ensured!
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "SELECT org_name, tier, active FROM tenants;"

init-db:
	@chcp 65001 >nul 2>&1
	@echo 🔄 Initializing database from scratch...
	@if not exist ".env" (echo ❌ ERROR: Missing .env file. Create one first! && exit /b 1)
	@docker-compose down -v >nul 2>&1
	@docker-compose up -d postgres
	@echo ⏳ Waiting for database to be ready (30s)...
	@timeout /t 30 /nobreak >nul
	@docker-compose build backend >nul
	@docker-compose run --rm backend alembic revision --autogenerate -m "initial_schema" || echo ⚠️ Migration skipped.
	@docker-compose run --rm backend alembic upgrade head
	@echo ✅ Database initialized successfully!

# --------------------------------------
# 🧩 Auto Repair & Reset Workflow
# --------------------------------------

fix-db:
	@chcp 65001 >nul 2>&1
	@echo 🧩 Running full database repair (PowerShell)...
	@powershell -ExecutionPolicy Bypass -NoProfile -File scripts/fix-db.ps1

# ✅ --- FIX 2: reset-db persistent alembic volume ---
reset-db:
	@chcp 65001 >nul 2>&1
	@echo 🔁 Full BuildToValue reset: containers + volumes + Alembic + migrations...
	@docker-compose down -v >nul 2>&1
	@if exist ".\alembic\versions" del /q .\alembic\versions\*.py >nul 2>&1
	@echo 🧹 Old migrations removed.
	@docker-compose up -d postgres >nul 2>&1
	@echo ⏳ Waiting for Postgres (15s)...
	@timeout /t 15 /nobreak >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d postgres -c "CREATE DATABASE buildtovalue OWNER btv_user;" >nul 2>&1 || echo (db already exists)
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;" >nul
	@echo ⚙️ Generating Alembic migration from current models...
	@docker-compose run --rm -v "%cd%/alembic:/app/alembic" backend alembic revision --autogenerate -m "auto_full_schema" >nul
	@echo 🚀 Applying migrations...
	@docker-compose run --rm -v "%cd%/alembic:/app/alembic" backend alembic upgrade head >nul
	@echo 💤 Waiting 5s to ensure schema visibility...
	@timeout /t 5 >nul
	@echo ✅ Database schema fully rebuilt!

# --------------------------------------
# 🚀 Startup Automation
# --------------------------------------

start: check-python
	@chcp 65001 >nul 2>&1
	@echo 🚀 ConciliaAI - Starting complete environment...
	@echo.
	@if not exist ".env" (echo ❌ ERROR: .env file not found. Please create it first! && exit /b 1)
	@echo 📦 Step 1/3: Resetting full environment...
	@$(MAKE) --no-print-directory reset-db
	@echo.
	@echo 🧱 Step 2/3: Ensuring default tenant...
	@$(MAKE) --no-print-directory init-tenant
	@echo.
	@echo 🩺 Step 3/3: Verifying backend health...
	@powershell -Command "Start-Sleep -Seconds 5; try { Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' -TimeoutSec 10 } catch { Write-Host '⚠️ Healthcheck failed, backend may still be starting.' }"
	@echo.
	@echo ✅ Environment ready!
	@echo 📍 API: http://localhost:8000
	@echo 📖 Docs: http://localhost:8000/docs
	@echo 🗄️ DB: postgresql://btv_user:btv_password@localhost:5432/buildtovalue
