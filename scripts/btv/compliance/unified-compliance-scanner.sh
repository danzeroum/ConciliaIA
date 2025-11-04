#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Unified Compliance Scanner
# Executa verificações de todos os frameworks de uma vez
set -euo pipefail

COMPLIANCE_DIR="scripts/compliance/frameworks"
UNIFIED_REPORT=".buildtovalue/compliance/reports/unified-compliance-$(date +%Y%m%d).json"

###############################################################################
# Executa scan de todos os frameworks
###############################################################################
run_all_scans() {
  echo "🔍 Executando scan de compliance unificado..."

  local results=()

  # GDPR
  echo ""
  echo "=== GDPR Compliance ==="
  if bash "$COMPLIANCE_DIR/gdpr/data-inventory.sh" validate >/dev/null 2>&1; then
    results+=('{"framework": "GDPR", "status": "compliant", "score": 100}')
    echo "✅ GDPR: Compliant"
  else
    results+=('{"framework": "GDPR", "status": "non_compliant", "score": 75}')
    echo "⚠️ GDPR: Non-compliant"
  fi

  # SOX
  echo ""
  echo "=== SOX Compliance ==="
  if bash "$COMPLIANCE_DIR/sox/audit-trail-validator.sh" validate >/dev/null 2>&1; then
    results+=('{"framework": "SOX", "status": "compliant", "score": 100}')
    echo "✅ SOX: Compliant"
  else
    results+=('{"framework": "SOX", "status": "non_compliant", "score": 80}')
    echo "⚠️ SOX: Non-compliant"
  fi

  # ISO 27001
  echo ""
  echo "=== ISO 27001 Compliance ==="
  bash "$COMPLIANCE_DIR/iso27001/isms-audit.sh" report >/dev/null 2>&1
  local iso_report=$(ls -t .buildtovalue/compliance/reports/iso27001-isms-audit-*.json | head -1)
  local iso_rate=$(jq -r '.summary.compliance_rate_percent' "$iso_report" 2>/dev/null || echo "0")

  if (( $(echo "$iso_rate >= 90" | bc -l) )); then
    results+=("{\"framework\": \"ISO27001\", \"status\": \"compliant\", \"score\": $iso_rate}")
    echo "✅ ISO 27001: Compliant ($iso_rate%)"
  else
    results+=("{\"framework\": \"ISO27001\", \"status\": \"partial\", \"score\": $iso_rate}")
    echo "⚠️ ISO 27001: Partial compliance ($iso_rate%)"
  fi

  printf '%s\n' "${results[@]}"
}

###############################################################################
# Gera relatório unificado
###############################################################################
generate_unified_report() {
  mkdir -p "$(dirname "$UNIFIED_REPORT")"

  echo ""
  echo "📊 Gerando relatório unificado..."

  local scans_json=$(run_all_scans | tail -3 | jq -s .)

  local compliant=$(echo "$scans_json" | jq '[.[] | select(.status == "compliant")] | length')
  local total=$(echo "$scans_json" | jq 'length')
  local avg_score=$(echo "$scans_json" | jq '[.[].score] | add / length')

  local report=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --argjson scans "$scans_json" \
    --arg compliant "$compliant" \
    --arg total "$total" \
    --arg avg "$avg_score" \
    '{
      report_date: $ts,
      report_type: "Unified Compliance Assessment",
      frameworks: $scans,
      summary: {
        total_frameworks: ($total | tonumber),
        compliant: ($compliant | tonumber),
        average_score: ($avg | tonumber),
        overall_status: (if ($compliant | tonumber) == ($total | tonumber) then "fully_compliant" elif ($compliant | tonumber) > 0 then "partially_compliant" else "non_compliant" end)
      },
      certification_readiness: {
        gdpr: (if (.frameworks[] | select(.framework == "GDPR") | .status) == "compliant" then "ready" else "not_ready" end),
        sox: (if (.frameworks[] | select(.framework == "SOX") | .status) == "compliant" then "ready" else "not_ready" end),
        iso27001: (if (.frameworks[] | select(.framework == "ISO27001") | .score) >= 90 then "ready" else "not_ready" end)
      }
    }'
  )

  echo "$report" | jq . > "$UNIFIED_REPORT"

  echo "✅ Relatório unificado gerado: $UNIFIED_REPORT"

  # Exibir resumo
  echo ""
  echo "╔════════════════════════════════════════╗"
  echo "║  Unified Compliance Summary            ║"
  echo "╠════════════════════════════════════════╣"
  echo "║  Overall Status: $(echo "$report" | jq -r '.summary.overall_status' | tr '[:lower:]' '[:upper:]' | awk '{printf "%-21s", $0}') ║"
  echo "║  Average Score:  $(echo "$report" | jq -r '.summary.average_score' | awk '{printf "%5.1f%%", $0}')                  ║"
  echo "║  Compliant:      $compliant/$total frameworks           ║"
  echo "╠════════════════════════════════════════╣"
  echo "║  Certification Readiness:              ║"
  echo "║    GDPR:     $(echo "$report" | jq -r '.certification_readiness.gdpr' | awk '{printf "%-27s", $0}') ║"
  echo "║    SOX:      $(echo "$report" | jq -r '.certification_readiness.sox' | awk '{printf "%-27s", $0}') ║"
  echo "║    ISO27001: $(echo "$report" | jq -r '.certification_readiness.iso27001' | awk '{printf "%-27s", $0}') ║"
  echo "╚════════════════════════════════════════╝"
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-scan}" in
    scan)
      run_all_scans | jq -s .
      ;;
    report)
      generate_unified_report
      ;;
    *)
      echo "Uso: $0 {scan|report}"
      exit 1
      ;;
  esac
fi
