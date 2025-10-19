.PHONY: help install test test-cov test-integration lint format run migrate seed docker-up docker-down

help:
@echo "ConciliaAI - Available commands:"
@echo "  make install           - Install dependencies"
@echo "  make test              - Run all tests"
@echo "  make test-integration  - Run integration tests only"
@echo "  make lint              - Run linters"
@echo "  make format            - Format code"
@echo "  make run               - Run API server"
@echo "  make migrate           - Run database migrations"
@echo "  make seed              - Seed database with sample data"
@echo "  make docker-up         - Start Docker containers"
@echo "  make docker-down       - Stop Docker containers"

install:
pip install -r requirements.txt
pip install -r requirements-dev.txt

test:
pytest tests/ -v

test-integration:
pytest tests/integration/ -v -m integration

test-cov:
pytest tests/ --cov=src --cov-report=html --cov-report=term

test-accuracy:
pytest tests/accuracy/ -v -m accuracy

lint:
flake8 src/ tests/
mypy src/

format:
black src/ tests/
isort src/ tests/

run:
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

migrate:
alembic upgrade head

migrate-create:
@read -p "Enter migration name: " name; \
alembic revision --autogenerate -m "$$name"

seed:
python scripts/seed_database.py

docker-up:
docker-compose up -d

docker-down:
docker-compose down

docker-logs:
docker-compose logs -f

docker-reset:
docker-compose down -v
docker-compose up -d
sleep 5
make migrate
make seed
