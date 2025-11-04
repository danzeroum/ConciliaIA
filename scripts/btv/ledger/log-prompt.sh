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
