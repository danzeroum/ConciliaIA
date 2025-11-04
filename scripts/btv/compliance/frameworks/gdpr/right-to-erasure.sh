#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - GDPR Right to Erasure (Right to be Forgotten)
set -euo pipefail

LEDGER=".buildtovalue/ledger.jsonl"
COST_LEDGER=".buildtovalue/cost-ledger.jsonl"
AUDIT_LOG=".buildtovalue/audit/erasure-log.jsonl"

################################################################################
# Procura dados de um usuário
################################################################################
search_user_data() {
  local user_id="$1"

  echo "🔍 Procurando dados do usuário: $user_id"

  local found_in=()

  # Buscar em ledger
  if [[ -f "$LEDGER" ]] && grep -q "$user_id" "$LEDGER" 2>/dev/null; then
    found_in+=("ledger.jsonl")
  fi

  # Buscar em cost ledger
  if [[ -f "$COST_LEDGER" ]] && grep -q "$user_id" "$COST_LEDGER" 2>/dev/null; then
    found_in+=("cost-ledger.jsonl")
  fi

  # Buscar em reports
  if [[ -d ".buildtovalue/reports" ]] && find .buildtovalue/reports -type f -exec grep -q "$user_id" {} \; 2>/dev/null; then
    found_in+=("reports/")
  fi

  # Buscar em audit
  if [[ -d ".buildtovalue/audit" ]] && find .buildtovalue/audit -type f -exec grep -q "$user_id" {} \; 2>/dev/null; then
    found_in+=("audit/")
  fi

  if [[ ${#found_in[@]} -eq 0 ]]; then
    echo "✅ Nenhum dado encontrado para usuário: $user_id"
    return 1
  fi

  echo "📊 Dados encontrados em: ${found_in[*]}"
  return 0
}

################################################################################
# Executa erasure (com backup)
################################################################################
execute_erasure() {
  local user_id="$1"
  local reason="${2:-User request}"

  echo "🗑️ Executando erasure para usuário: $user_id"
  echo "   Motivo: $reason"

  # Criar backup antes da erasure
  local backup_dir=".buildtovalue/compliance/erasure-backups/$(date +%Y%m%d-%H%M%S)-$user_id"
  mkdir -p "$backup_dir"

  echo "💾 Criando backup em: $backup_dir"

  # Backup de ledgers
  if [[ -f "$LEDGER" ]]; then
    grep "$user_id" "$LEDGER" > "$backup_dir/ledger-backup.jsonl" 2>/dev/null || true
  fi

  if [[ -f "$COST_LEDGER" ]]; then
    grep "$user_id" "$COST_LEDGER" > "$backup_dir/cost-ledger-backup.jsonl" 2>/dev/null || true
  fi

  # Executar erasure
  echo "🔥 Removendo dados..."

  # Remover de ledger (substituir por [REDACTED])
  if [[ -f "$LEDGER" ]]; then
    sed -i.bak "s/$user_id/[REDACTED-GDPR]/g" "$LEDGER"
  fi

  if [[ -f "$COST_LEDGER" ]]; then
    sed -i.bak "s/$user_id/[REDACTED-GDPR]/g" "$COST_LEDGER"
  fi

  # Remover reports relacionados
  if [[ -d ".buildtovalue/reports" ]]; then
    find .buildtovalue/reports -type f -exec grep -l "$user_id" {} \; 2>/dev/null | while read -r file; do
      echo "  🗑️ Removendo: $file"
      rm -f "$file"
    done
  fi

  # Registrar erasure no audit log
  mkdir -p "$(dirname "$AUDIT_LOG")"

  local audit_entry=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg user "$user_id" \
    --arg reason "$reason" \
    --arg backup "$backup_dir" \
    '{
      "timestamp": $ts,
      "action": "gdpr_erasure",
      "user_id": $user,
      "reason": $reason,
      "backup_location": $backup,
      "status": "completed"
    }'
  )

  echo "$audit_entry" >> "$AUDIT_LOG"

  echo "✅ Erasure concluída"
  echo "📁 Backup disponível em: $backup_dir"
  echo "📋 Auditoria registrada em: $AUDIT_LOG"
}

################################################################################
# Gera relatório de erasure
################################################################################
generate_erasure_report() {
  if [[ ! -f "$AUDIT_LOG" ]]; then
    echo "⚠️ Nenhum registro de erasure encontrado"
    return 0
  fi

  echo "📊 Relatório de GDPR Erasure Requests"
  echo "======================================"

  local total=$(jq -s 'length' "$AUDIT_LOG")
  echo "Total de requests: $total"

  echo ""
  echo "Requests recentes:"
  jq -r '.timestamp + " | " + .user_id + " | " + .reason' "$AUDIT_LOG" | tail -10
}

################################################################################
# Modo de uso
################################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    search)
      search_user_data "${2:?User ID required}"
      ;;
    erase)
      if search_user_data "${2:?User ID required}"; then
        # Em modo não interativo (CI), 'yes' é usado
        if [[ -t 0 ]]; then
            read -p "Confirmar erasure para '${2}'? (yes/no): " confirm
        else
            echo "Modo não interativo detectado, aceitando 'yes'..."
            confirm="yes"
        fi

        if [[ "$confirm" == "yes" ]]; then
          execute_erasure "${2}" "${3:-User request}"
        else
          echo "❌ Erasure cancelada"
        fi
      fi
      ;;
    report)
      generate_erasure_report
      ;;
    *)
      echo "Uso: $0 {search|erase|report} [user_id] [reason]"
      echo ""
      echo "Exemplos:"
      echo "  $0 search user@example.com"
      echo "  $0 erase user@example.com 'GDPR Art. 17 request'"
      echo "  $0 report"
      exit 1
      ;;
  esac
fi
