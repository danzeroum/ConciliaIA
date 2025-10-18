# ====================================
# BuildToValue v7 - Makefile
# ====================================

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
@make docker-up

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
@make migrate
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
