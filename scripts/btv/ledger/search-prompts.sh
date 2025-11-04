#!/usr/bin/env bash
set -euo pipefail

QUERY="${1:-}"
[ -z "$QUERY" ] && { echo "usage: $0 <query>"; exit 2; }

INDEX=".buildtovalue/ledger/prompts/index.jsonl"
[ ! -f "$INDEX" ] && { echo "❌ Nenhum prompt registrado ainda."; exit 1; }

echo "🔍 Buscando: '$QUERY'"
echo ""

# Busca case-insensitive em task, keywords e persona
jq -r --arg q "${QUERY,,}" '
  select(
    (.task | ascii_downcase | contains($q)) or
    (.keywords | ascii_downcase | contains($q)) or
    (.persona | ascii_downcase | contains($q))
  ) |
  "ID: \(.id)\nData: \(.timestamp)\nPersona: \(.persona)\nTask: \(.task)\nTamanho: \(.prompt_size_bytes) bytes\nArquivo: \(.prompt_file)\n---"
' "$INDEX"

MATCHES=$(jq -r --arg q "${QUERY,,}" '
  select(
    (.task | ascii_downcase | contains($q)) or
    (.keywords | ascii_downcase | contains($q)) or
    (.persona | ascii_downcase | contains($q))
  ) | .id
' "$INDEX" | wc -l | tr -d ' ')

echo ""
echo "📊 $MATCHES prompt(s) encontrado(s)"
echo ""
echo "💡 Ver prompt completo: zcat .buildtovalue/ledger/prompts/<ID>.md.gz"
