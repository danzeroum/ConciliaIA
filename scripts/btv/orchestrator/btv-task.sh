#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Executor Local Governado
# Camadas: Concurrency → Ethics → IA-dupla → Sandbox → CI/CD
set -euo pipefail

TASK_DESC="$1"
WORKDIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Importar módulos
source "$WORKDIR/scripts/orchestrator/task-lock-manager.sh"
source "$WORKDIR/scripts/orchestrator/sandbox-executor.sh"
source "$WORKDIR/scripts/providers/ia-provider-manager.sh"

LEDGER="$WORKDIR/.buildtovalue/ledger.jsonl"
REPORT_DIR="$WORKDIR/.buildtovalue/reports"
LOCK_NAME="btv-task-$(echo "$TASK_DESC" | md5sum | cut -d' ' -f1)"

mkdir -p "$REPORT_DIR"

###############################################################################
# NOVA SEÇÃO: Concurrency Control
###############################################################################
echo "🔒 Adquirindo lock de execução..."
if ! acquire_lock "$LOCK_NAME"; then
  echo "❌ Não foi possível adquirir lock. Outra instância já está processando esta tarefa."
  exit 1
fi

# Lock será liberado automaticamente ao sair (trap configurado em task-lock-manager.sh)

###############################################################################
# Rate limiting + circuit breaker (mantido do v7.3)
###############################################################################
rate_limit_check() {
  local max_per_hour=50
  local current=$(grep "$(date +%Y-%m-%dT%H)" "$LEDGER" 2>/dev/null | wc -l)
  if [[ $current -ge $max_per_hour ]]; then
    echo "⚠️ Rate limit atingido ($current/$max_per_hour por hora)."
    exit 1
  fi
}

check_global_breaker() {
  local fails=$(grep '"result": "failure"' "$LEDGER" | tail -n 5 | wc -l)
  if [[ $fails -ge 5 ]]; then
    echo "⛔ Circuit breaker global ativado. Pausando 10 min."
    sleep 600
    exit 1
  fi
}

###############################################################################
# MPAA Execution com Prompt Integrity (ATUALIZADO)
###############################################################################
execute_with_mpaa() {
  echo "🔐 Assinando prompt para validação de integridade..."
  local prompt_hash=$(python3 "$WORKDIR/scripts/governance/prompt-signer.py" "$TASK_DESC")
  
  echo "🤖 IA-A gerando código..."
  local gen_output="$REPORT_DIR/iaA_output.txt"
  generate_with_fallback "$TASK_DESC" > "$gen_output"
  
  echo "🕵️ IA-B auditando resultado..."
  local audit_output="$REPORT_DIR/iaB_audit.txt"
  audit_with_provider "$(cat "$gen_output")" > "$audit_output"
  
  echo "⚖️ Validando integridade e comparando saídas (MPAA)..."
  python3 "$WORKDIR/scripts/governance/mpaa-validator.py" \
    "$gen_output" "$audit_output" "$REPORT_DIR/mpaa_result.json" "$prompt_hash"
  
  local divergence=$(jq -r '.divergence_score' "$REPORT_DIR/mpaa_result.json")
  if (( $(echo "$divergence > 0.25" | bc -l) )); then
    echo "⚠️ Divergência IA-A ↔ IA-B > 0.25. Requer revisão humana."
    log_to_ledger "mpaa_rejected" "$divergence"
    exit 1
  fi
  
  echo "✅ MPAA audit OK (divergência: $divergence). Prosseguindo para sandbox..."
  sandbox_execute "$gen_output"
}

###############################################################################
# Log estruturado no ledger
###############################################################################
log_to_ledger() {
  local status="$1"
  local details="${2:-}"
  
  local entry=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg task "$TASK_DESC" \
    --arg status "$status" \
    --arg details "$details" \
    --arg pid "$$" \
    --arg lock "$LOCK_NAME" \
    '{
      timestamp: $ts,
      task: $task,
      status: $status,
      details: $details,
      pid: $pid,
      lock: $lock
    }'
  )
  
  echo "$entry" >> "$LEDGER"
}

###############################################################################
# Execução Principal
###############################################################################
echo "🚀 BuildToValue v7.4-Platinum - Executor Local Governado"
echo "📋 Tarefa: $TASK_DESC"

rate_limit_check
check_global_breaker
execute_with_mpaa

log_to_ledger "success"
echo "✅ Tarefa concluída com sucesso."
