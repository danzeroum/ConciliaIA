#!/bin/bash
# =====================================================================
#  BuildToValue v7.1 - Ledger Export Utility
#  scripts/ledger/export.sh
# ---------------------------------------------------------------------
#  Função:
#    Exporta as decisões registradas no Ledger BuildToValue (.jsonl)
#    para um arquivo JSON estruturado e legível pelo Codex.
#
#  Compatibilidade:
#    - Chamado por: orchestrator/sync-ledger-to-codex.sh
#    - Baseado em: ledger_policies (governance.yaml)
#
#  Segurança:
#    ✔ Read-only (não altera ledger original)
#    ✔ Sem dependências externas (usa jq ou Python disponível no ambiente)
#    ✔ Conformidade com shell_allowlist
#
#  Última atualização: 2025-10-30
# =====================================================================

set -e

OUTPUT_FILE=".buildtovalue/ledger/export-latest.json"
PERIOD="current"
FORMAT="json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output=*) OUTPUT_FILE="${1#*=}" ;;
    --period=*) PERIOD="${1#*=}" ;;
    --format=*) FORMAT="${1#*=}" ;;
    *) echo "⚠️  Argumento desconhecido: $1" ;;
  esac
  shift
done

LEDGER_DIR=".buildtovalue/ledger/decisions"
mkdir -p "$(dirname "$OUTPUT_FILE")"

if [ ! -d "$LEDGER_DIR" ]; then
  echo "❌ Diretório de decisões não encontrado: $LEDGER_DIR"
  exit 1
fi

shopt -s nullglob
LEDGER_FILES=("$LEDGER_DIR"/*.jsonl)
shopt -u nullglob

if [ ${#LEDGER_FILES[@]} -eq 0 ]; then
  echo "⚠️  Nenhuma decisão encontrada no ledger."
  printf '[]\n' > "$OUTPUT_FILE"
  exit 0
fi

TMP_FILE=$(mktemp)

if command -v jq >/dev/null 2>&1; then
  jq -s '.' "${LEDGER_FILES[@]}" > "$TMP_FILE"
else
  python3 - "$TMP_FILE" "${LEDGER_FILES[@]}" <<'PY'
import json
import sys
from pathlib import Path

tmp_path = Path(sys.argv[1])
file_paths = sys.argv[2:]
records = []

for path in file_paths:
    with open(path, 'r', encoding='utf-8') as fh:
        buffer = ""
        brace_count = 0
        for line in fh:
            if not line.strip():
                continue
            brace_count += line.count('{') - line.count('}')
            buffer += line
            if brace_count == 0 and buffer:
                records.append(json.loads(buffer))
                buffer = ""
        if buffer.strip():
            records.append(json.loads(buffer))

tmp_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
PY
fi

mv "$TMP_FILE" "$OUTPUT_FILE"

echo "✅ Ledger exportado com sucesso para $OUTPUT_FILE"
exit 0
