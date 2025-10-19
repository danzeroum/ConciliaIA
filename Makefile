.PHONY: help setup install test test-cov test-integration test-accuracy test-performance test-load test-load-k6 test-stress test-all benchmark lint format run migrate migrate-create seed docker-up docker-down docker-logs docker-reset

help:
@echo "ConciliaAI - Available commands:"
@echo "  make setup              - Install dependencies and prepare environment"
@echo "  make install            - Install dependencies"
@echo "  make test               - Run unit + integration tests"
@echo "  make test-integration   - Run integration tests only"
@echo "  make test-cov           - Run tests with coverage"
@echo "  make test-accuracy      - Run accuracy validation"
@echo "  make test-performance   - Run performance benchmarks"
@echo "  make test-stress        - Run stress tests"
@echo "  make test-load          - Run load tests (Locust)"
@echo "  make test-load-k6       - Run load tests (K6)"
@echo "  make test-all           - Run full automated test suite"
@echo "  make benchmark          - Run pytest benchmarks"
@echo "  make lint               - Run linters"
@echo "  make format             - Format code"
@echo "  make run                - Run API server"
@echo "  make migrate            - Run database migrations"
@echo "  make seed               - Seed database with sample data"
@echo "  make docker-up          - Start Docker containers"
@echo "  make docker-down        - Stop Docker containers"
@echo "  make docker-logs        - Tail Docker logs"
@echo "  make docker-reset       - Reset Docker environment"

setup: install docker-up
	sleep 5
	$(MAKE) migrate

install:
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install pytest-benchmark locust

test:
pytest tests/unit/ tests/integration/ -v

test-integration:
pytest tests/integration/ -v -m integration

test-cov:
pytest tests/ --cov=src --cov-report=html --cov-report=term

test-accuracy:
pytest tests/accuracy/ -v -m accuracy

test-performance:
pytest tests/performance/ -v -m performance

test-load:
chmod +x scripts/run_load_tests.sh
./scripts/run_load_tests.sh

test-load-k6:
chmod +x scripts/run_k6_load_tests.sh
./scripts/run_k6_load_tests.sh

test-stress:
pytest tests/stress/ -v -m stress

test-all:
@echo "🧪 Running complete test suite..."
@$(MAKE) test
@$(MAKE) test-accuracy
@$(MAKE) test-performance
@$(MAKE) test-stress
@echo "✅ All tests completed!"

benchmark:
pytest tests/performance/ --benchmark-only --benchmark-autosave

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
$(MAKE) migrate
$(MAKE) seed
