#!/usr/bin/env bash
set -e

echo "🧩 BuildToValue DB Auto-Fix (Linux/CI)"
docker-compose down -v >/dev/null 2>&1 || true
docker volume rm conciliaai_postgres_data -f >/dev/null 2>&1 || true

echo "🐘 Starting PostgreSQL..."
docker-compose up -d postgres
sleep 10

echo "🔍 Checking if database 'conciliaai' exists..."
if ! docker exec buildtovalue-postgres psql -U btv_user -tAc "SELECT 1 FROM pg_database WHERE datname='conciliaai';" | grep -q 1; then
  echo "🆕 Creating database conciliaai..."
  docker exec -it buildtovalue-postgres psql -U btv_user -c "CREATE DATABASE conciliaai;"
else
  echo "✅ Database conciliaai already exists."
fi

echo "🗄️ Applying Alembic migrations..."
docker-compose run --rm backend alembic upgrade head

echo "🌱 Running seed_database.py..."
docker-compose run --rm backend python scripts/seed_database.py

echo "🚀 Starting backend..."
docker-compose up -d backend
sleep 10

echo "⏳ Waiting for API healthcheck..."
for i in {1..20}; do
  if curl -fsS http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "✅ API is healthy!"
    curl -s http://localhost:8000/api/v1/health | jq .
    exit 0
  fi
  echo "Waiting..."
  sleep 3
done

echo "❌ API did not respond after 20 tries."
docker logs conciliaai-backend --tail 40
exit 1
