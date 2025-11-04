#!/usr/bin/env bash
# Utilitário para verificar integridade de prompts em lote
set -euo pipefail

AUDIT_DIR=".buildtovalue/audit"

check_all_prompts() {
  echo "🔍 Verificando integridade de prompts..."
  local total=0
  local valid=0
  local invalid=0
  
  for audit_file in "$AUDIT_DIR"/prompt-*.json; do
    [[ -f "$audit_file" ]] || continue
    
    total=$((total + 1))
    local hash=$(jq -r '.signature.hash' "$audit_file")
    local prompt=$(jq -r '.prompt' "$audit_file")
    
    if python3 scripts/governance/prompt-signer.py "$prompt" | grep -q "$hash"; then
      valid=$((valid + 1))
    else
      invalid=$((invalid + 1))
      echo "  ❌ Integridade comprometida: $audit_file"
    fi
  done
  
  echo "✅ Total: $total | Válidos: $valid | Inválidos: $invalid"
  
  if [[ $invalid -gt 0 ]]; then
    return 1
  fi
  
  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  check_all_prompts
fi