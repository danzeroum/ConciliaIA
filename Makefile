.PHONY: help setup install start check-python fix-pip test test-cov test-integration test-accuracy test-performance test-load test-load-k6 test-stress test-all benchmark lint format run migrate migrate-create generate-migration seed docker-up docker-down docker-logs docker-reset init-db

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
	@rem Check if migrations exist
	@if not exist "alembic\versions\*.py" (
		@echo ⚠️  No migrations found! Running init-db...
		@$(MAKE) --no-print-directory init-db
	) else (
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
	)

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

# Generate migration automatically from models
generate-migration:
	@chcp 65001 >nul 2>&1
	@echo 🔄 Generating migration from models...
	@docker-compose down -v
	@docker-compose up -d postgres
	@timeout /t 5 /nobreak >nul
	@docker-compose build backend
	@docker-compose run --rm backend python -m alembic revision --autogenerate -m "auto generated schema"
	@echo ✅ Migration generated! Check alembic/versions/
	@echo.
	@echo Next: make start

seed:
	@chcp 65001 >nul 2>&1
	@echo Seeding database with sample data...
	@docker exec conciliaai-backend python scripts/seed_database.py
	@echo ✅ Database seeded successfully

init-db:
	@chcp 65001 >nul 2>&1
	@echo 🔄 Initializing database from scratch...
	@powershell -ExecutionPolicy Bypass -File scripts/init-db.ps1
	@echo ✅ Database initialized!

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
# ====================================
# BuildToValue v7 - Makefile
.PHONY: help install test lint format clean docker-up docker-down migrate seed
# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
# Default target
.DEFAULT_GOAL := help
# Help
help: ## Show this help message
@echo "BuildToValue v7 - Available Commands:"
@echo ""
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
# Installation
install: ## Install dependencies
@echo "📦 Installing dependencies..."
$(PIP) install -r requirements.txt
@echo "✅ Dependencies installed!"
install-dev: ## Install development dependencies
@echo "📦 Installing dev dependencies..."
$(PIP) install -r requirements-dev.txt
@echo "✅ Dev dependencies installed!"
# Setup
setup: ## Complete setup (install + docker + migrate)
@echo "🚀 Setting up BuildToValue v7..."
@make install
@make docker-up
@sleep 10
@make migrate
@echo "✅ Setup complete!"
# Docker
docker-up: ## Start Docker containers
@echo "🐳 Starting Docker containers..."
docker-compose up -d
@echo "✅ Containers started!"
docker-down: ## Stop Docker containers
@echo "🐳 Stopping Docker containers..."
docker-compose down
@echo "✅ Containers stopped!"
docker-restart: ## Restart Docker containers
@make docker-down
docker-logs: ## Show Docker logs
docker-compose logs -f
# Database
migrate: ## Run database migrations
@echo "🗄️  Running migrations..."
$(PYTHON) scripts/python/migrate.py
@echo "✅ Migrations complete!"
seed: ## Seed database with test data
@echo "🌱 Seeding database..."
$(PYTHON) scripts/python/seed_database.py
@echo "✅ Database seeded!"
db-reset: ## Reset database (drop + migrate + seed)
@echo "⚠️  Resetting database..."
./scripts/database/reset.sh
@make seed
@echo "✅ Database reset!"
# Testing
test: ## Run tests
@echo "🧪 Running tests..."
$(PYTEST) tests/ -v
@echo "✅ Tests complete!"
test-cov: ## Run tests with coverage
@echo "🧪 Running tests with coverage..."
$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term
@echo "✅ Coverage report generated!"
@echo "📊 Open htmlcov/index.html to view report"
test-watch: ## Run tests in watch mode
$(PYTEST) tests/ -v --looponfail
# Code Quality
lint: ## Run linters
@echo "🔍 Running linters..."
$(FLAKE8) src/ tests/
$(MYPY) src/
@echo "✅ Linting complete!"
format: ## Format code
@echo "🎨 Formatting code..."
$(BLACK) src/ tests/ scripts/
$(ISORT) src/ tests/ scripts/
@echo "✅ Code formatted!"
format-check: ## Check code formatting
@echo "🔍 Checking code format..."
$(BLACK) --check src/ tests/ scripts/
$(ISORT) --check-only src/ tests/ scripts/
# Security
security-scan: ## Run security scan
@echo "🔒 Running security scan..."
bandit -r src/
@echo "✅ Security scan complete!"
# Scripts
fix-permissions: ## Fix script permissions
@echo "🔧 Fixing script permissions..."
find scripts/ -name "*.sh" -exec chmod +x {} \;
@echo "✅ Permissions fixed!"
# Health Check
health: ## Run health check
@echo "🏥 Running health check..."
./scripts/troubleshooting/health-check.sh
# Development
dev: ## Start development server
@echo "🚀 Starting development server..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
dev-debug: ## Start development server with debug
@echo "🐛 Starting debug server..."
DEBUG=true uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
# Building
build: ## Build Docker images
@echo "🏗️  Building Docker images..."
docker-compose build
@echo "✅ Build complete!"
# Cleaning
clean: ## Clean temporary files
@echo "🧹 Cleaning..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete
@echo "✅ Cleaned!"
clean-all: clean docker-down ## Clean everything including Docker
@echo "🧹 Deep cleaning..."
docker system prune -af --volumes
@echo "✅ Everything cleaned!"
# Documentation
docs: ## Build documentation
@echo "📚 Building documentation..."
mkdocs build
@echo "✅ Documentation built!"
docs-serve: ## Serve documentation locally
@echo "📚 Serving documentation..."
mkdocs serve
# Release
release-patch: ## Release patch version (x.x.X)
@echo "🚀 Releasing patch version..."
./scripts/release.sh patch
release-minor: ## Release minor version (x.X.0)
@echo "🚀 Releasing minor version..."
./scripts/release.sh minor
release-major: ## Release major version (X.0.0)
@echo "🚀 Releasing major version..."
./scripts/release.sh major
# Utilities
logs: ## Show application logs
tail -f .buildtovalue/logs/app.log
stats: ## Show quick statistics
@./scripts/monitoring/quick-stats.sh
validate: ## Validate configuration
@echo "✅ Validating configuration..."
$(PYTHON) scripts/python/validate_config.py
# All-in-one commands
all: clean install docker-up migrate test ## Run everything
@echo "✅ All tasks complete!"
ci: format-check lint test ## CI pipeline
@echo "✅ CI checks passed!"
