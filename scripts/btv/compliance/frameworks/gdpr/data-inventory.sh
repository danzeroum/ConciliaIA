#!/usr/bin/env bash
# ===============================================================
# BuildToValue v7.4-Platinum - GDPR Data Inventory
# ===============================================================
# Description:
#   Gera e valida o inventário de dados pessoais processados
#   conforme os requisitos do GDPR (Art. 30).
#
# Modes:
#   scan       → Escaneia fontes e detecta categorias de dados pessoais
#   generate   → Cria inventário estruturado JSON (modo principal)
#   validate   → Valida integridade e campos obrigatórios
#   report     → Exporta relatório Markdown legível
# ===============================================================

set -euo pipefail

MODE="${1:-help}"

INVENTORY_FILE=".buildtovalue/compliance/reports/gdpr-data-inventory.json"
LEDGER_FILE=".buildtovalue/ledger.jsonl"
REPORT_DIR=".buildtovalue/compliance/reports"
mkdir -p "$(dirname "$INVENTORY_FILE")" "$REPORT_DIR"

print_usage() {
  echo "Uso: $0 {scan|generate|validate|report}"
  exit 1
}

# ---------------------------------------------------------------
# SCAN MODE – detecta padrões de dados pessoais
# ---------------------------------------------------------------
scan_personal_data() {
  echo "🔍 [GDPR]: Escaneando dados pessoais..."

  local sources=(
    "$LEDGER_FILE"
    ".buildtovalue/cost-ledger.jsonl"
    ".buildtovalue/audit"
    ".buildtovalue/reports"
  )

  local patterns=(
    "email"
    "ip_address"
    "user_id"
    "username"
    "session_id"
  )

  local found=()
  for src in "${sources[@]}"; do
    [[ -e "$src" ]] || continue
    for pat in "${patterns[@]}"; do
      if grep -riq "$pat" "$src" 2>/dev/null; then
        found+=("$pat")
      fi
    done
  done

  local unique=($(printf "%s\n" "${found[@]}" | sort -u))
  echo "✅ [GDPR]: Detectadas ${#unique[@]} categorias."
  printf "%s\n" "${unique[@]}"
}

# ---------------------------------------------------------------
# GENERATE MODE – cria o inventário estruturado
# ---------------------------------------------------------------
generate_inventory() {
  echo "📋 [GDPR]: Gerando inventário de dados..."
  local categories
  categories=$(scan_personal_data | jq -R . | jq -s .)

  jq -n \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson categories "$categories" \
    '{
      version: "1.0",
      generated_at: $ts,
      data_controller: {
        name: "BuildToValue Organization",
        contact: "dpo@buildtovalue.com"
      },
      personal_data_categories: $categories,
      retention_policy: "90 days (default)",
      encryption: "At rest (AES-256 simulated)",
      storage: ".buildtovalue/",
      dpia_required: false
    }' | jq . > "$INVENTORY_FILE"

  echo "✅ [GDPR]: Inventário salvo em: $INVENTORY_FILE"
}

# ---------------------------------------------------------------
# VALIDATE MODE – verifica campos obrigatórios
# ---------------------------------------------------------------
validate_inventory() {
  echo "🧪 [GDPR]: Validando inventário..."
  if [[ ! -f "$INVENTORY_FILE" ]]; then
    echo "❌ [GDPR]: Inventário não encontrado. Execute '$0 generate' antes."
    exit 1
  fi

  local required=(
    ".data_controller"
    ".personal_data_categories"
    ".retention_policy"
  )

  local missing=()
  for field in "${required[@]}"; do
    if ! jq -e "$field" "$INVENTORY_FILE" >/dev/null 2>&1; then
      missing+=("$field")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    echo "✅ [GDPR]: Inventário válido."
    exit 0
  else
    echo "❌ [GDPR]: Campos ausentes:"
    printf '  - %s\n' "${missing[@]}"
    exit 1
  fi
}

# ---------------------------------------------------------------
# REPORT MODE – exporta relatório Markdown
# ---------------------------------------------------------------
export_inventory_report() {
  local report="$REPORT_DIR/gdpr-inventory-report-$(date -u +%Y%m%dT%H%M%SZ).md"
  echo "🧾 [GDPR]: Gerando relatório Markdown..."

  jq -r '
    "# GDPR Data Inventory Report",
    "**Generated:** \(.generated_at)",
    "**Controller:** \(.data_controller.name) (\(.data_controller.contact))",
    "",
    "## Categories:",
    (.personal_data_categories[]? | "- " + .),
    "",
    "## Retention Policy:",
    .retention_policy,
    "",
    "## Encryption:",
    .encryption,
    "",
    "*BuildToValue v7.4-Platinum – Automatic Compliance Module*"
  ' "$INVENTORY_FILE" > "$report"

  echo "✅ [GDPR]: Relatório exportado: $report"
}

# ---------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------
case "$MODE" in
  scan)      scan_personal_data ;;
  generate)  generate_inventory ;;
  validate)  validate_inventory ;;
  report)    export_inventory_report ;;
  *)         print_usage ;;
esac
