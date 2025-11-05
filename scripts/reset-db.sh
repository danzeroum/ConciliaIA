#!/usr/bin/env bash
# ==========================================================
# 🧠 ConciliaAI / BuildToValue - Database Reset Script
# Autor: BuildToValue Automation
# Versão: 1.0
# Descrição:
#   Limpa containers e volumes, recria o Postgres a partir
#   do init.sql e aplica todas as migrações automaticamente.
# ==========================================================

set -e  # para o script se ocorrer algum erro

echo "🧹 Limpando containers e volumes anteriores..."
docker-compose down -v >/dev/null 2>&1 || true
docker volume rm conciliaai_postgres_data --force >/dev/null 2>&1 || true

echo "🚀 Subindo o container Postgres..."
docker-compose up -d postgres

echo "⏳ Aguardando o Postgres ficar saudável (até 60s)..."
timeout=60
elapsed=0

while [ $elapsed -lt $timeout ]; do
    status=$(docker inspect -f "{{.State.Health.Status}}" buildtovalue-postgres 2>/dev/null || echo "starting")
    if [ "$status" = "healthy" ]; then
        echo "✅ Postgres está saudável!"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ "$status" != "healthy" ]; then
    echo "❌ Postgres não ficou saudável após 60 segundos. Abortando."
    exit 1
fi

echo "🧩 Verificando extensões instaladas..."
docker exec -it buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dx"

echo "⚙️ Aplicando migrações Alembic..."
docker-compose run --rm backend alembic upgrade head

echo "✅ Migrações aplicadas com sucesso!"
echo "📊 Tabelas criadas:"
docker exec -it buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dt"

echo "🎉 Banco de dados do ConciliaAI pronto!"
