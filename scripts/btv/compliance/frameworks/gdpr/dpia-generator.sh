#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - GDPR DPIA Generator
# Gera um Relatório de Avaliação de Impacto de Proteção de Dados (DPIA)
# Em conformidade com ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM

set -euo pipefail

# --- Configuração ---
INVENTORY_FILE=".buildtovalue/compliance/reports/gdpr-data-inventory.json"
REPORT_FILE=".buildtovalue/compliance/reports/gdpr-dpia-report.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Funções ---

log() {
    echo "🛡️  [GDPR DPIA]: $1"
}

# Valida se o inventário de dados existe
validate_inventory() {
    if [[ ! -f "$INVENTORY_FILE" ]]; then
        log "Erro: Inventário de dados não encontrado em $INVENTORY_FILE"
        log "Execute data-inventory.sh primeiro."
        exit 1
    fi
    log "Inventário de dados encontrado. Analisando..."
}

# Gera o relatório DPIA baseado no inventário
generate_dpia_report() {
    mkdir -p "$(dirname "$REPORT_FILE")"

    # Extrai dados do inventário
    local purpose
    purpose=$(jq -r '.personal_data_categories[0].purpose // "N/A"' "$INVENTORY_FILE")
    local types_found
    types_found=$(jq -r '.personal_data_categories[0].types_found // []' "$INVENTORY_FILE")

    # Lógica de Risco (Simplificada para Nível Platinum)
    local risk_level="LOW"
    local risk_description="Processamento de dados operacionais básicos (user_id)."

    if [[ $(echo "$types_found" | jq 'length') -gt 1 ]] || \
       [[ $(echo "$types_found" | jq '. | index("email")') != "null" ]]; then
        risk_level="MEDIUM"
        risk_description="Processamento de PII (ex: email, IP) detectado. Risco de exposição."
    fi

    # Gerar o JSON do DPIA
    # Correção: Removida a concatenação + $ts que causava erro de sintaxe jq
    jq -n \
        --arg ts "$TIMESTAMP" \
        --arg purpose "$purpose" \
        --argjson types "$types_found" \
        --arg risk_level "$risk_level" \
        --arg risk_desc "$risk_description" \
        '{
            "btv_spec": "ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM",
            "framework": "GDPR-DPIA",
            "report_id": ("DPIA-" + $ts),
            "generated_at": $ts,
            "inventory_ref": "'"$INVENTORY_FILE"'",
            "processing_activity": $purpose,
            "data_involved": $types,
            "consultation_with_dpo": true,
            "risks": [
                {
                    "risk_id": "DPIA-RISK-001",
                    "description": $risk_desc,
                    "likelihood": $risk_level,
                    "impact": "MEDIUM",
                    "inherent_risk_score": (if $risk_level == "MEDIUM" then 15 else 5 end),
                    "mitigation_measures": [
                        "Redação de PII no ledger (PII Guardian)",
                        "Políticas de retenção de dados",
                        "Controles de acesso baseados em função (RBAC)",
                        "Logs de auditoria (SOX)"
                    ],
                    "residual_risk_level": (if $risk_level == "MEDIUM" then "LOW" else "LOW" end)
                }
            ],
            "overall_risk_level": $risk_level,
            "approval": {
                "dpo_approval": "PENDING",
                "date": null
            }
        }' > "$REPORT_FILE"
}

# --- Execução Principal ---
main() {
    validate_inventory
    generate_dpia_report
    log "Relatório DPIA gerado: $REPORT_FILE"
}

main "$@"
