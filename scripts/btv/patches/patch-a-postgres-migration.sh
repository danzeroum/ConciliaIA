#!/bin/bash
# PATCH-A: Migração do Ledger para PostgreSQL
set -euo pipefail

echo "🔧 PATCH-A: Migrando Ledger de .jsonl para PostgreSQL"
echo "==========================================================="

# 1. Criar schema no PostgreSQL
cat > scripts/database/init-ledger-schema.sql <<'SQL'
-- BuildToValue v7.1 - Ledger Schema
CREATE TABLE IF NOT EXISTS ledger_decisions (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    agent VARCHAR(100) NOT NULL,
    task TEXT NOT NULL,
    outcome VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2),
    automated BOOLEAN DEFAULT false,
    source VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ledger_timestamp ON ledger_decisions(timestamp DESC);
CREATE INDEX idx_ledger_agent ON ledger_decisions(agent);
CREATE INDEX idx_ledger_outcome ON ledger_decisions(outcome);

-- Tabela de prompts (substituindo os arquivos .jsonl)
CREATE TABLE IF NOT EXISTS ledger_prompts (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    persona VARCHAR(100) NOT NULL,
    task TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    response_text TEXT,
    prompt_sha256 VARCHAR(64),
    response_sha256 VARCHAR(64),
    keywords TEXT[],
    mode VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prompts_persona ON ledger_prompts(persona);
CREATE INDEX idx_prompts_timestamp ON ledger_prompts(timestamp DESC);
CREATE INDEX idx_prompts_keywords ON ledger_prompts USING GIN(keywords);
SQL

# 2. Aplicar schema no banco
echo "📊 Aplicando schema no PostgreSQL..."
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue < scripts/database/init-ledger-schema.sql

# 3. Migrar dados existentes (.jsonl -> PostgreSQL)
echo "📦 Migrando dados existentes..."
python3 - <<'PY'
import json
import psycopg2
from pathlib import Path
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    database="buildtovalue",
    user="btv_user",
    password="changeme123"
)
cur = conn.cursor()

# Migrar decisões
ledger_dir = Path(".buildtovalue/ledger/decisions")
if ledger_dir.exists():
    for jsonl_file in ledger_dir.glob("*.jsonl"):
        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        cur.execute("""
                            INSERT INTO ledger_decisions 
                            (id, timestamp, agent, task, outcome, confidence, automated, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            record.get('id'),
                            record.get('timestamp'),
                            record.get('agent'),
                            record.get('task'),
                            record.get('outcome'),
                            record.get('confidence'),
                            record.get('automated', False),
                            record.get('source', 'legacy')
                        ))
                    except Exception as e:
                        print(f"⚠️  Erro ao migrar registro: {e}")

conn.commit()
cur.close()
conn.close()
print("✅ Migração concluída")
PY

# 4. Atualizar auto-log-decision.sh para escrever no PostgreSQL
cat > scripts/ledger/auto-log-decision.sh <<'LOGSH'
#!/usr/bin/env bash
set -euo pipefail

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
LOGSH

chmod +x scripts/ledger/auto-log-decision.sh

# 5. Atualizar log-prompt.sh para escrever no PostgreSQL
cat > scripts/ledger/log-prompt.sh <<'PROMPTSH'
#!/usr/bin/env bash
set -euo pipefail

ID="${1:-PROMPT-$(date +%Y%m%d-%H%M%S)}"
PERSONA="${2:-unknown}"
TASK="${3:-no task}"
MODE="${4:-manual}"

echo "📝 Cole o PROMPT (Ctrl-D para finalizar):"
PROMPT_TEXT=$(cat)

echo "📝 Cole a RESPOSTA (opcional, Ctrl-D para pular):"
RESPONSE_TEXT=$(cat || echo "")

# Calcular checksums
PROMPT_SHA=$(echo "$PROMPT_TEXT" | sha256sum | cut -d' ' -f1)
RESPONSE_SHA=$(echo "$RESPONSE_TEXT" | sha256sum | cut -d' ' -f1)

# Extrair keywords
KEYWORDS=$(echo "$PROMPT_TEXT" | grep -oE '[[:alnum:]_]{4,}' | head -n 50 | tr '\n' ',' | sed 's/,$//')

# Inserir no PostgreSQL
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue <<SQL
INSERT INTO ledger_prompts 
(id, timestamp, persona, task, prompt_text, response_text, prompt_sha256, response_sha256, keywords, mode)
VALUES 
('$ID', '$(date -Iseconds)', '$PERSONA', '$TASK', 
 \$\$${PROMPT_TEXT}\$\$, \$\$${RESPONSE_TEXT}\$\$,
 '$PROMPT_SHA', '$RESPONSE_SHA', 
 string_to_array('$KEYWORDS', ','), '$MODE');
SQL

echo "✅ Prompt registrado: $ID"
PROMPTSH

chmod +x scripts/ledger/log-prompt.sh

echo ""
echo "✅ PATCH-A concluído: Ledger agora usa PostgreSQL"
echo "   - Schema criado: ledger_decisions + ledger_prompts"
echo "   - Dados migrados de .jsonl para PostgreSQL"
echo "   - Scripts atualizados: auto-log-decision.sh, log-prompt.sh"
