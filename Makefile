.PHONY: help setup install start check-python fix-pip test test-cov test-integration test-accuracy test-performance test-load test-load-k6 test-stress test-all benchmark lint format run migrate migrate-create seed docker-up docker-down docker-logs docker-reset

SHELL := cmd.exe
.SHELLFLAGS := /c

help:
	@chcp 65001 >nul 2>&1
	@echo ConciliaAI - Available commands:
	@echo.
	@echo 🚀 Quick Start:
	@echo   make start              - Complete setup (install + docker + migrate + seed)
	@echo.
	@echo 📦 Setup:
	@echo   make setup              - Install dependencies and prepare environment
	@echo   make install            - Install Python dependencies
	@echo   make check-python       - Verify Python and Docker installation
	@echo   make fix-pip            - Install/repair pip if needed
	@echo.
	@echo 🐳 Docker:
	@echo   make docker-up          - Start Docker containers
	@echo   make docker-down        - Stop Docker containers
	@echo   make docker-logs        - Tail Docker logs
	@echo   make docker-reset       - Reset Docker environment
	@echo.
	@echo 🗄️ Database:
	@echo   make migrate            - Run database migrations
	@echo   make migrate-create     - Create new migration
	@echo   make seed               - Seed database with sample data
	@echo.
	@echo 🧪 Testing:
	@echo   make test               - Run unit + integration tests
	@echo   make test-integration   - Run integration tests only
	@echo   make test-cov           - Run tests with coverage
	@echo   make test-accuracy      - Run accuracy validation
	@echo   make test-performance   - Run performance benchmarks
	@echo   make test-stress        - Run stress tests
	@echo   make test-all           - Run full automated test suite
	@echo.
	@echo 🔧 Development:
	@echo   make run                - Run API server locally
	@echo   make lint               - Run linters
	@echo   make format             - Format code
	@echo.
	@echo 📊 Monitoring:
	@echo   make benchmark          - Run pytest benchmarks

check-python:
	@chcp 65001 >nul 2>&1
	@echo 🔍 Checking prerequisites...
	@where python >nul 2>&1 || (echo ❌ Python not found. Install Python 3.11 from https://www.python.org && exit /b 1)
	@where docker >nul 2>&1 || (echo ❌ Docker not found. Install from https://www.docker.com && exit /b 1)
	@python --version | findstr /C:"3.11" >nul || python --version | findstr /C:"3.12" >nul || (echo ⚠️  WARNING: Python 3.11-3.12 recommended. Current version: && python --version && timeout /t 3 >nul)
	@echo ✅ Prerequisites OK

fix-pip:
	@chcp 65001 >nul 2>&1
	@echo 🔧 Checking pip installation...
	@python -m pip --version >nul 2>&1 && echo ✅ Pip OK || (echo 📥 Installing pip... && python -m ensurepip --default-pip)
	@python -m pip install --upgrade pip setuptools wheel

start: check-python
	@chcp 65001 >nul 2>&1
	@echo 🚀 ConciliaAI - Starting complete environment...
	@echo.
	@echo 📦 Step 1/5: Installing dependencies...
	@$(MAKE) --no-print-directory install
	@echo.
	@echo 🐳 Step 2/5: Starting Docker containers...
	@$(MAKE) --no-print-directory docker-up
	@echo.
	@echo ⏳ Step 3/5: Waiting for database...
	@timeout /t 10 /nobreak >nul
	@echo.
	@echo 🗄️ Step 4/5: Running migrations...
	@$(MAKE) --no-print-directory migrate
	@echo.
	@echo 🌱 Step 5/5: Seeding database...
	@$(MAKE) --no-print-directory seed
	@echo.
	@echo ✅ Environment ready!
	@echo.
	@echo 📍 API: http://localhost:8000
	@echo 📖 Docs: http://localhost:8000/docs
	@echo 🗄️ DB: postgresql://btv_user:btv_password@localhost:5432/conciliaai
	@echo.
	@echo 🎯 Next steps:
	@echo    - Access API docs: http://localhost:8000/docs
	@echo    - Run tests: make test
	@echo    - View logs: make docker-logs
	@echo.

setup: install docker-up
	@timeout /t 5 /nobreak >nul
	@$(MAKE) migrate

install: fix-pip
	@chcp 65001 >nul 2>&1
	@echo 📦 Installing dependencies...
	@python -m pip install -r requirements.txt
	@python -m pip install -r requirements-dev.txt
	@python -m pip install pytest-benchmark locust
	@echo ✅ Dependencies installed

test:
	@pytest tests/unit/ tests/integration/ -v

test-integration:
	@pytest tests/integration/ -v -m integration

test-cov:
	@pytest tests/ --cov=src --cov-report=html --cov-report=term

test-accuracy:
	@pytest tests/accuracy/ -v -m accuracy

test-performance:
	@pytest tests/performance/ -v -m performance

test-load:
	@chmod +x scripts/run_load_tests.sh
	@./scripts/run_load_tests.sh

test-load-k6:
	@chmod +x scripts/run_k6_load_tests.sh
	@./scripts/run_k6_load_tests.sh

test-stress:
	@pytest tests/stress/ -v -m stress

test-all:
	@chcp 65001 >nul 2>&1
	@echo 🧪 Running complete test suite...
	@$(MAKE) test
	@$(MAKE) test-accuracy
	@$(MAKE) test-performance
	@$(MAKE) test-stress
	@echo ✅ All tests completed!

benchmark:
	@pytest tests/performance/ --benchmark-only --benchmark-autosave

lint:
	@flake8 src/ tests/
	@mypy src/

format:
	@black src/ tests/
	@isort src/ tests/

run:
	@uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	@chcp 65001 >nul 2>&1
	@echo Running database migrations...
	@docker exec conciliaai-backend python -m alembic upgrade head
	@echo ✅ Migrations completed

migrate-create:
	@set /p name="Enter migration name: " && docker exec conciliaai-backend python -m alembic revision --autogenerate -m "%name%"

seed:
@chcp 65001 >nul 2>&1
@echo Seeding database with sample data...
@docker exec conciliaai-backend python scripts/seed_database.py
@echo ✅ Database seeded successfully

docker-up:
	@docker-compose up -d
	@echo ⏳ Waiting for services to be ready...
	@timeout /t 5 /nobreak >nul
	@docker-compose ps

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f

docker-reset:
	@docker-compose down -v
	@docker-compose up -d
	@timeout /t 5 /nobreak >nul
	@$(MAKE) migrate
	@$(MAKE) seed
