#!/usr/bin/env bash
set -euo pipefail


LEDGER_FILE=".buildtovalue/ledger.jsonl"
ARCHIVE_DIR=".buildtovalue/archives"

echo "🏥 BuildToValue Ledger Health Check"
echo "===================================="

# 1. Verificar ledger atual
echo ""
echo "📋 Ledger Atual:"
if [[ -f "$LEDGER_FILE" ]]; then
  entries=$(wc -l < "$LEDGER_FILE")
  size=$(get_size_mb "$LEDGER_FILE" 2>/dev/null || echo "0")
  echo "  ✅ Arquivo existe"
  echo "  📊 Entradas: $entries"
  echo "  💾 Tamanho: ${size}MB"

  # Validar JSON
  if jq empty "$LEDGER_FILE" 2>/dev/null; then
    echo "  ✅ Formato JSON válido"
  else
    echo "  ❌ Formato JSON inválido!"
  fi
else
  echo "  ⚠️ Arquivo não encontrado"
fi

# 2. Verificar archives
echo ""
echo "📦 Archives:"
if [[ -d "$ARCHIVE_DIR" ]]; then
  archive_count=$(find "$ARCHIVE_DIR" -name "ledger-*.jsonl.gz" | wc -l)
  echo "  📊 Total de archives: $archive_count"

  # Verificar integridade dos últimos 5
  echo "  🔍 Verificando integridade dos últimos 5 archives..."
  find "$ARCHIVE_DIR" -name "ledger-*.jsonl.gz" -type f | sort -r | head -5 | while read -r archive; do
    if gzip -t "$archive" 2>/dev/null; then
      echo "    ✅ $(basename "$archive")"
    else
      echo "    ❌ $(basename "$archive") - CORROMPIDO"
    fi
  done
else
  echo "  ⚠️ Diretório de archives não encontrado"
fi

# 3. Estatísticas de uso
echo ""
echo "📊 Estatísticas:"
if [[ -f "$LEDGER_FILE" ]]; then
  success=$(grep -c '"result": "success"' "$LEDGER_FILE" 2>/dev/null || echo "0")
  failure=$(grep -c '"result": "failure"' "$LEDGER_FILE" 2>/dev/null || echo "0")
  total=$((success + failure))

  if [[ $total -gt 0 ]]; then
    success_rate=$(awk "BEGIN {printf \"%.2f\", ($success / $total) * 100}")
    echo "  ✅ Sucessos: $success ($success rate%)"
echo "  ❌ Falhas: $failure"
echo "  📈 Taxa de sucesso: $success_rate%"
fi
fi
echo ""
echo "===================================="
echo "✅ Health check concluído"
