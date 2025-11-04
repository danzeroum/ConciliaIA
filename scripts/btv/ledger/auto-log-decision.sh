#!/usr/bin/env bash
set -euo pipefail

# --- BuildToValue v7.1 Resilience Fallback ---
if ! docker ps --format "{{.Names}}" | grep -q "^buildtovalue-postgres$"; then
  echo "⚠️  Container buildtovalue-postgres não encontrado — iniciando localmente..."
  docker run -d --name buildtovalue-postgres \
    -e POSTGRES_USER=btv_user -e POSTGRES_PASSWORD=changeme123 -e POSTGRES_DB=buildtovalue \
    -p 5432:5432 postgres:16
  sleep 10
fi

AGENT="${1:-unknown}"
TASK="${2:-no task specified}"
OUTCOME="${3:-success}"
CONFIDENCE="${4:-0.90}"

DECISION_ID="DEC-$(date +%Y%m%d-%H%M%S)"
TIMESTAMP=$(date -Iseconds)

# Escrever no PostgreSQL
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue <<SQL
INSERT INTO ledger_decisions 
(id, timestamp, agent, task, outcome, confidence, automated, source)
VALUES 
('$DECISION_ID', '$TIMESTAMP', '$AGENT', '$TASK', '$OUTCOME', $CONFIDENCE, true, 'auto-log');
SQL

echo "✅ Decision logged: $DECISION_ID"
