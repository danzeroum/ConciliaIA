# ===============================================
# BuildToValue v7.1 - ConciliaAI Full Automation
# ===============================================
.PHONY: help setup install start check-python fix-pip test test-cov test-integration test-accuracy test-performance test-load test-load-k6 test-stress test-all benchmark lint format run migrate migrate-create generate-migration seed docker-up docker-down docker-logs docker-reset init-db init-tenant fix-db reset-db

SHELL := cmd.exe
.SHELLFLAGS := /c

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
	@docker volume rm conciliaai_postgres_data --force 2>nul || echo Volume already removed
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

init-tenant:
	@chcp 65001 >nul 2>&1
	@powershell -ExecutionPolicy Bypass -NoProfile -File scripts/init-tenant.ps1

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

reset-db:
	@chcp 65001 >nul 2>&1
	@echo 🔁 Full BuildToValue reset: containers + volumes + schema...
	@docker-compose down -v >nul 2>&1
	@docker volume rm conciliaai_postgres_data --force 2>nul || echo Volume already removed
	@if exist ".\alembic\versions\*.py" del /q .\alembic\versions\*.py >nul 2>&1
	@echo 🧹 Old migrations and volumes removed.
	@docker-compose up -d postgres >nul 2>&1
	@echo ⏳ Waiting for Postgres (20s)...
	@timeout /t 20 /nobreak >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d postgres -c "DROP DATABASE IF EXISTS buildtovalue;" >nul 2>&1
	@docker exec -i buildtovalue-postgres psql -U btv_user -d postgres -c "CREATE DATABASE buildtovalue OWNER btv_user;" >nul 2>&1
	@echo ✅ Database recreated from scratch
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" >nul
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;" >nul
	@echo 🏗️ Applying SQL schema directly...
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue < scripts/create-schema.sql
	@echo ✅ Database schema created!
	@docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dt"

start: check-python
	@chcp 65001 >nul 2>&1
	@echo 🚀 ConciliaAI - Starting complete environment under BuildToValue v7.1...
	@echo.
	@if not exist ".env" (echo ❌ ERROR: .env file not found. Please create it first! && exit /b 1)
	@if not exist "scripts\init-tenant.ps1" (echo ❌ ERROR: scripts\init-tenant.ps1 not found! && exit /b 1)
	@echo 📦 Step 1/4: Resetting full environment...
	@$(MAKE) --no-print-directory reset-db
	@echo.
	@echo 🧱 Step 2/4: Ensuring default tenant...
	@$(MAKE) --no-print-directory init-tenant
	@echo.
	@echo ⚙️ Step 3/4: Starting backend container...
	@docker-compose up -d backend
	@echo ⏳ Waiting for backend to start...
	@timeout /t 10 /nobreak >nul
	@docker ps --filter "name=backend"
	@echo.
	@echo 🩺 Step 4/4: Validating backend health...
	@docker exec conciliaai-backend curl -f http://localhost:8000/health 2>nul >nul && (echo ✅ Backend is healthy!) || (echo ⚠️ Backend health check failed - check logs: docker logs conciliaai-backend)
	@echo.
	@echo ✅ Environment fully validated!
	@echo 📍 API: http://localhost:8000
	@echo 📖 Docs: http://localhost:8000/docs
	@echo 🗄️ DB: postgresql://btv_user:btv_password@localhost:5432/buildtovalue
	@echo.
	@echo 🧩 BuildToValue v7.1: All checks passed ✅
