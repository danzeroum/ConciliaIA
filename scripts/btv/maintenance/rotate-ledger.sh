#!/usr/bin/env bash
# ==============================================================
# BuildToValue v7.4-Platinum - Ledger Rotation Utility
# Script: scripts/maintenance/rotate-ledger.sh
# Objetivo: Rotacionar ledger quando excede o tamanho máximo configurado
# Dependência externa removida (bc → awk)
# ==============================================================
set -euo pipefail

LEDGER_DIR="${BTV_LEDGER_DIR:-.buildtovalue/ledger}"
ARCHIVE_DIR="${BTV_ARCHIVE_DIR:-.buildtovalue/archives}"
MAX_SIZE_MB="${BTV_MAX_LEDGER_SIZE_MB:-5}"   # Limite padrão: 5MB
DATE_TAG=$(date -u +"%Y%m%d-%H%M%S")

mkdir -p "$LEDGER_DIR" "$ARCHIVE_DIR"

LEDGER_FILE="$LEDGER_DIR/ledger.jsonl"
ARCHIVE_FILE="$ARCHIVE_DIR/ledger-$DATE_TAG.jsonl.gz"

###############################################################################
# 🔹 Função: calcular tamanho em MB (sem bc)
###############################################################################
get_size_mb() {
  local file="$1"
  local size_bytes
  size_bytes=$(stat -c%s "$file" 2>/dev/null || echo 0)
  awk "BEGIN {printf \"%.2f\", $size_bytes / 1024 / 1024}"
}

###############################################################################
# 🔹 Função: rotacionar ledger
###############################################################################
rotate_ledger() {
  local size_mb
  size_mb=$(get_size_mb "$LEDGER_FILE")

  echo "📏 Ledger atual: ${size_mb}MB (limite: ${MAX_SIZE_MB}MB)"
  if (( $(awk "BEGIN {print ($size_mb > $MAX_SIZE_MB)}") )); then
    echo "⚙️  Rotacionando ledger excedente..."
    mv "$LEDGER_FILE" "$LEDGER_FILE.tmp"

    gzip -c "$LEDGER_FILE.tmp" > "$ARCHIVE_FILE"
    rm -f "$LEDGER_FILE.tmp"

    echo "✅ Ledger rotacionado e arquivado como: $ARCHIVE_FILE"

    # Gerar hash para integridade
    sha256sum "$ARCHIVE_FILE" | awk '{print $1}' > "$ARCHIVE_FILE.sha256"
    echo "🔒 Checksum gerado: $ARCHIVE_FILE.sha256"

    # Criar novo ledger vazio
    echo "{}" > "$LEDGER_FILE"
    echo "🧾 Novo ledger inicializado: $LEDGER_FILE"
  else
    echo "✅ Ledger dentro do limite. Nenhuma rotação necessária."
  fi
}

###############################################################################
# 🔹 Execução principal
###############################################################################
echo "🚀 Iniciando verificação de rotação do ledger..."
if [[ ! -f "$LEDGER_FILE" ]]; then
  echo "{}" > "$LEDGER_FILE"
  echo "ℹ️  Ledger inexistente — arquivo inicial criado."
fi

rotate_ledger

echo "🏁 Rotação concluída com sucesso."
