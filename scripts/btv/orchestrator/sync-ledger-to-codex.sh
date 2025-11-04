#!/bin/bash
# =====================================================================
#  BuildToValue v7.1 - Orchestrator Script
#  sync-ledger-to-codex.sh
# ---------------------------------------------------------------------
#  Função:
#    Sincroniza as decisões registradas no Ledger local com o Codex
#    (repositório de decisões do pipeline CI/CD).
#
#  Compatibilidade:
#    - IA-ASSISTANT-PROTOCOL.md (sec. 9)
#    - LEDGER_POLICIES (governance.yaml)
#    - CI/CD Foundation Gates (scripts/gates-v7.sh)
#
#  Segurança:
#    ✔ Nenhum comando destrutivo (rm, sudo, chmod 777)
#    ✔ Apenas leitura/exportação de ledger
#    ✔ Conformidade com shell_allowlist
#
#  Última atualização: 2025-10-30
# =====================================================================

set -e

IA_NAME=""
ARTIFACT_PATH=""
FORCE_MODE=false
OUTPUT_FILE=".buildtovalue/ledger/export-latest.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ia=*) IA_NAME="${1#*=}" ;;
    --artifact=*) ARTIFACT_PATH="${1#*=}" ;;
    --force) FORCE_MODE=true ;;
    *) echo "⚠️  Argumento desconhecido: $1" ;;
  esac
  shift
done

echo "🔄 Iniciando sincronização do ledger com Codex..."
echo "   IA: ${IA_NAME:-não informada}"
echo "   Artefato: ${ARTIFACT_PATH:-não informado}"
echo ""

if [ ! -f "./scripts/ledger/export.sh" ]; then
  echo "❌ Erro: script ./scripts/ledger/export.sh não encontrado."
  echo "   Impossível exportar ledger."
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "📦 Exportando ledger atual para JSON..."
./scripts/ledger/export.sh --format=json --period=current --output="$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
  echo "✅ Ledger exportado com sucesso: $OUTPUT_FILE"
else
  echo "❌ Falha ao gerar $OUTPUT_FILE"
  exit 1
fi

if [ "$FORCE_MODE" = true ]; then
  echo "🚀 Forçando atualização no Codex (modo local simulado)..."
  echo "$(date -Iseconds) | SYNC | ${IA_NAME:-unknown} | ${ARTIFACT_PATH:-none}" \
    >> .buildtovalue/ledger/sync-history.log
  echo "✅ Registro de sincronização criado em .buildtovalue/ledger/sync-history.log"
else
  echo "ℹ️  Execução em modo não forçado. Nenhuma modificação remota aplicada."
fi

echo ""
echo "🎯 Ledger sincronizado com Codex (simulado localmente com sucesso)."
exit 0
