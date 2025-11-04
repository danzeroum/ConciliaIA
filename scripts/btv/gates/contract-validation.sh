#!/bin/bash
# Gate: verificar se contratos existem e são válidos

set -euo pipefail

# ========================================
# BYPASS TEMPORÁRIO PARA TESTES
# ========================================
if [[ "${SKIP_CONTRACT_VALIDATION:-false}" == "true" ]]; then
  echo "⚠️  Contract validation SKIPPED (SKIP_CONTRACT_VALIDATION=true)"
  exit 0
fi

if [[ "${FREE_MODE_ENABLED:-false}" == "true" ]]; then
  echo "ℹ️  Contract validation SKIPPED (FREE_MODE_ENABLED=true)"
  exit 0
fi

# ========================================
# VALIDAÇÃO NORMAL
# ========================================

SPECS_DIR=".buildtovalue/specifications"

if [[ ! -f .buildtovalue/config/governance.yaml ]]; then
  echo "⚠️  Governance configuration not found, skipping validation"
  exit 0
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "⚠️  yq not installed. Skipping contract enforcement checks." >&2
  exit 0
fi

# Verificar se a política está habilitada
POLICY_ENABLED=$(yq eval '.specification_policy.enabled // false' .buildtovalue/config/governance.yaml 2>/dev/null)

if [[ "$POLICY_ENABLED" != "true" ]]; then
  echo "ℹ️  Specification policy disabled, skipping validation"
  exit 0
fi

REQUIRED_SPECS=$(yq eval '.specification_policy.required_specs[]' .buildtovalue/config/governance.yaml 2>/dev/null || true)

if [[ -z "$REQUIRED_SPECS" ]]; then
  echo "ℹ️  No required specs defined."
  exit 0
fi

for spec in $REQUIRED_SPECS; do
  if [[ ! -f "$SPECS_DIR/$spec" ]]; then
    echo "❌ Missing required spec: $spec" >&2
    exit 1
  fi

  ./scripts/specification/validate-contract.sh "$SPECS_DIR/$spec"
done

echo "✅ All contracts validated"
