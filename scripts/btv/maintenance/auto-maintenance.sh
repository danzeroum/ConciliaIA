#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Manutenção Automática
# Executar via cron: 0 2 * * * /path/to/auto-maintenance.sh
set -euo pipefail

WORKDIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$WORKDIR"

LOG_FILE=".buildtovalue/maintenance.log"
REPORT_FILE=".buildtovalue/maintenance-report.json"

###############################################################################
# Logger estruturado
###############################################################################
log() {
  local level="$1"
  shift
  local message="$*"
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

###############################################################################
# Executa tarefa de manutenção com error handling
###############################################################################
run_maintenance_task() {
  local task_name="$1"
  local task_command="$2"
  
  log "INFO" "Iniciando tarefa: $task_name"
  
  local start_time=$(date +%s)
  local status="success"
  local error_msg=""
  
  if ! eval "$task_command" 2>&1 | tee -a "$LOG_FILE"; then
    status="failure"
    error_msg="Comando falhou: $task_command"
    log "ERROR" "$error_msg"
  fi
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  # Registrar no relatório
  local entry=$(jq -n \
    --arg task "$task_name" \
    --arg status "$status" \
    --arg duration "$duration" \
    --arg error "$error_msg" \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    '{
      timestamp: $ts,
      task: $task,
      status: $status,
      duration_seconds: ($duration | tonumber),
      error: $error
    }'
  )
  
  if [[ -f "$REPORT_FILE" ]]; then
    jq --argjson entry "$entry" '. += [$entry]' "$REPORT_FILE" > "${REPORT_FILE}.tmp"
    mv "${REPORT_FILE}.tmp" "$REPORT_FILE"
  else
    echo "[$entry]" > "$REPORT_FILE"
  fi
  
  log "INFO" "Tarefa $task_name concluída em ${duration}s com status: $status"
}

###############################################################################
# Tarefas de manutenção
###############################################################################

maintenance_cleanup_orphan_locks() {
  run_maintenance_task "cleanup_orphan_locks" \
    "bash scripts/orchestrator/task-lock-manager.sh cleanup"
}

maintenance_rotate_ledger() {
  run_maintenance_task "rotate_ledger" \
    "bash scripts/maintenance/rotate-ledger.sh rotate"
}

maintenance_cleanup_archives() {
  run_maintenance_task "cleanup_old_archives" \
    "bash scripts/maintenance/cleanup-archives.sh"
}

maintenance_validate_prompt_integrity() {
  run_maintenance_task "validate_prompt_integrity" \
    "bash scripts/governance/prompt-integrity-checker.sh"
}

maintenance_health_check() {
  run_maintenance_task "health_check" \
    "bash scripts/maintenance/ledger-health-check.sh"
}

maintenance_cost_report() {
  run_maintenance_task "cost_report" \
    "bash scripts/providers/ia-provider-manager.sh cost-report"
}

maintenance_compress_old_reports() {
  log "INFO" "Comprimindo reports antigos (>7 dias)..."
  find .buildtovalue/reports -name "*.txt" -type f -mtime +7 -exec gzip {} \;
  find .buildtovalue/reports -name "*.json" -type f -mtime +7 -exec gzip {} \;
}

maintenance_prune_cost_ledger() {
  # Manter apenas últimos 90 dias no cost ledger
  local cost_ledger=".buildtovalue/cost-ledger.jsonl"
  
  if [[ -f "$cost_ledger" ]]; then
    local cutoff_date=$(date -u -d '90 days ago' +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
                        date -u -v-90d +"%Y-%m-%dT%H:%M:%SZ")
    
    jq -c "select(.timestamp >= \"$cutoff_date\")" "$cost_ledger" > "${cost_ledger}.tmp"
    mv "${cost_ledger}.tmp" "$cost_ledger"
    
    log "INFO" "Cost ledger filtrado (mantidos últimos 90 dias)"
  fi
}

###############################################################################
# Relatório de métricas
###############################################################################
generate_metrics_summary() {
  log "INFO" "Gerando sumário de métricas..."
  
  local ledger=".buildtovalue/ledger.jsonl"
  local cost_ledger=".buildtovalue/cost-ledger.jsonl"
  
  local metrics=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg total_tasks "$(grep -c . "$ledger" 2>/dev/null || echo 0)" \
    --arg success_rate "$(awk '/"result": "success"/{s++} END{print s/NR*100}' "$ledger" 2>/dev/null || echo 0)" \
    --arg total_cost "$(jq -s 'map(.cost_usd) | add' "$cost_ledger" 2>/dev/null || echo 0)" \
    --arg active_locks "$(find .buildtovalue/locks -name "*.lock" 2>/dev/null | wc -l)" \
    --arg ledger_size_mb "$(du -m "$ledger" 2>/dev/null | cut -f1 || echo 0)" \
    --arg archives_count "$(find .buildtovalue/archives -name "*.gz" 2>/dev/null | wc -l)" \
    '{
      timestamp: $ts,
      total_tasks: ($total_tasks | tonumber),
      success_rate: ($success_rate | tonumber),
      total_cost_usd: ($total_cost | tonumber),
      active_locks: ($active_locks | tonumber),
      ledger_size_mb: ($ledger_size_mb | tonumber),
      archives_count: ($archives_count | tonumber)
    }'
  )
  
  echo "$metrics" > .buildtovalue/metrics-summary.json
  log "INFO" "Métricas: $(echo "$metrics" | jq -c .)"
}

###############################################################################
# Notificação (opcional)
###############################################################################
send_maintenance_notification() {
  local status="$1"
  local summary="$2"
  
  # Webhook (Slack, Discord, etc.)
  if [[ -n "${BTV_WEBHOOK_URL:-}" ]]; then
    curl -X POST "$BTV_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{
        \"text\": \"BuildToValue Maintenance Report\",
        \"status\": \"$status\",
        \"summary\": \"$summary\"
      }" 2>/dev/null || true
  fi
  
  # Email (via sendmail)
  if command -v sendmail &>/dev/null && [[ -n "${BTV_ALERT_EMAIL:-}" ]]; then
    echo -e "Subject: BuildToValue Maintenance Report\n\n$summary" | \
      sendmail "$BTV_ALERT_EMAIL" 2>/dev/null || true
  fi
}

###############################################################################
# Execução principal
###############################################################################
main() {
  log "INFO" "========================================="
  log "INFO" "BuildToValue v7.4 - Manutenção Automática"
  log "INFO" "========================================="
  
  # Resetar relatório
  echo "[]" > "$REPORT_FILE"
  
  # Executar tarefas
  maintenance_cleanup_orphan_locks
  maintenance_rotate_ledger
  maintenance_cleanup_archives
  maintenance_validate_prompt_integrity
  maintenance_health_check
  maintenance_cost_report
  maintenance_compress_old_reports
  maintenance_prune_cost_ledger
  
  # Gerar métricas
  generate_metrics_summary
  
  # Analisar resultado
  local failures=$(jq '[.[] | select(.status == "failure")] | length' "$REPORT_FILE")
  local total=$(jq 'length' "$REPORT_FILE")
  
  log "INFO" "========================================="
  log "INFO" "Manutenção concluída: $((total - failures))/$total tarefas bem-sucedidas"
  
  if [[ $failures -gt 0 ]]; then
    log "WARN" "$failures tarefa(s) falharam. Verifique $REPORT_FILE"
    send_maintenance_notification "WARNING" "$failures falhas detectadas"
    exit 1
  else
    log "INFO" "Todas as tarefas executadas com sucesso"
    send_maintenance_notification "SUCCESS" "Manutenção completada sem erros"
  fi
}

main "$@"