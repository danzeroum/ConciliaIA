#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Metrics Collector
# Coleta métricas para Prometheus/Grafana
set -euo pipefail

METRICS_FILE="${BTV_METRICS_FILE:-/var/local/btv-metrics.prom}"
LEDGER=".buildtovalue/ledger.jsonl"
COST_LEDGER=".buildtovalue/cost-ledger.jsonl"

###############################################################################
# Calcula métricas do ledger
###############################################################################
calculate_ledger_metrics() {
  if [[ ! -f "$LEDGER" ]]; then
    echo "0"
    return
  fi
  
  local total_tasks=$(wc -l < "$LEDGER")
  local success_count=$(grep -c '"result": "success"' "$LEDGER" 2>/dev/null || echo "0")
  local failure_count=$(grep -c '"result": "failure"' "$LEDGER" 2>/dev/null || echo "0")
  
  local success_rate=0
  if [[ $total_tasks -gt 0 ]]; then
    success_rate=$(awk "BEGIN {printf \"%.2f\", ($success_count / $total_tasks) * 100}")
  fi
  
  echo "$total_tasks|$success_count|$failure_count|$success_rate"
}

###############################################################################
# Calcula métricas MPAA
###############################################################################
calculate_mpaa_metrics() {
  local reports_dir=".buildtovalue/reports"
  
  if [[ ! -d "$reports_dir" ]]; then
    echo "0|0|0"
    return
  fi
  
  local total_validations=$(find "$reports_dir" -name "mpaa_result.json" | wc -l)
  local approved=0
  local rejected=0
  local avg_divergence=0
  
  if [[ $total_validations -gt 0 ]]; then
    # Contar aprovados/rejeitados
    for result in "$reports_dir"/mpaa_result.json*; do
      [[ -f "$result" ]] || continue
      local decision=$(jq -r '.decision' "$result" 2>/dev/null || echo "unknown")
      
      if [[ "$decision" == "approve" ]]; then
        approved=$((approved + 1))
      elif [[ "$decision" == "reject" ]]; then
        rejected=$((rejected + 1))
      fi
    done
    
    # Calcular divergência média
    avg_divergence=$(jq -s 'map(.divergence_score) | add / length' "$reports_dir"/mpaa_result.json* 2>/dev/null || echo "0")
  fi
  
  echo "$total_validations|$approved|$rejected|$avg_divergence"
}

###############################################################################
# Calcula métricas de custo
###############################################################################
calculate_cost_metrics() {
  if [[ ! -f "$COST_LEDGER" ]]; then
    echo "0|0|0"
    return
  fi
  
  local total_cost=$(jq -s 'map(.cost_usd) | add' "$COST_LEDGER" 2>/dev/null || echo "0")
  local total_requests=$(jq -s 'length' "$COST_LEDGER" 2>/dev/null || echo "0")
  local avg_cost=0
  
  if [[ $total_requests -gt 0 ]]; then
    avg_cost=$(awk "BEGIN {printf \"%.4f\", $total_cost / $total_requests}")
  fi
  
  echo "$total_cost|$total_requests|$avg_cost"
}

###############################################################################
# Calcula métricas de locks
###############################################################################
calculate_lock_metrics() {
  local lock_dir=".buildtovalue/locks"
  
  if [[ ! -d "$lock_dir" ]]; then
    echo "0|0"
    return
  fi
  
  local active_locks=$(find "$lock_dir" -name "*.lock" -type f | wc -l)
  local orphan_locks=0
  
  for pid_file in "$lock_dir"/*.pid 2>/dev/null; do
    [[ -f "$pid_file" ]] || continue
    local pid=$(cat "$pid_file")
    
    if ! kill -0 "$pid" 2>/dev/null; then
      orphan_locks=$((orphan_locks + 1))
    fi
  done
  
  echo "$active_locks|$orphan_locks"
}

###############################################################################
# Gera arquivo Prometheus
###############################################################################
generate_prometheus_metrics() {
  # Header
  cat > "$METRICS_FILE" <<EOF
# HELP btv_tasks_total Total number of tasks executed
# TYPE btv_tasks_total counter
# HELP btv_tasks_success_total Total number of successful tasks
# TYPE btv_tasks_success_total counter
# HELP btv_tasks_failure_total Total number of failed tasks
# TYPE btv_tasks_failure_total counter
# HELP btv_success_rate_percent Task success rate percentage
# TYPE btv_success_rate_percent gauge
# HELP btv_mpaa_validations_total Total MPAA validations
# TYPE btv_mpaa_validations_total counter
# HELP btv_mpaa_approved_total MPAA validations approved
# TYPE btv_mpaa_approved_total counter
# HELP btv_mpaa_rejected_total MPAA validations rejected
# TYPE btv_mpaa_rejected_total counter
# HELP btv_mpaa_avg_divergence Average MPAA divergence score
# TYPE btv_mpaa_avg_divergence gauge
# HELP btv_cost_total_usd Total cost in USD
# TYPE btv_cost_total_usd counter
# HELP btv_cost_requests_total Total API requests
# TYPE btv_cost_requests_total counter
# HELP btv_cost_avg_per_request Average cost per request
# TYPE btv_cost_avg_per_request gauge
# HELP btv_locks_active Active locks count
# TYPE btv_locks_active gauge
# HELP btv_locks_orphan Orphan locks count
# TYPE btv_locks_orphan gauge
EOF

  # Ledger metrics
  IFS='|' read -r total success failure rate <<< "$(calculate_ledger_metrics)"
  cat >> "$METRICS_FILE" <<EOF
btv_tasks_total $total
btv_tasks_success_total $success
btv_tasks_failure_total $failure
btv_success_rate_percent $rate
EOF

  # MPAA metrics
  IFS='|' read -r validations approved rejected divergence <<< "$(calculate_mpaa_metrics)"
  cat >> "$METRICS_FILE" <<EOF
btv_mpaa_validations_total $validations
btv_mpaa_approved_total $approved
btv_mpaa_rejected_total $rejected
btv_mpaa_avg_divergence $divergence
EOF

  # Cost metrics
  IFS='|' read -r cost requests avg <<< "$(calculate_cost_metrics)"
  cat >> "$METRICS_FILE" <<EOF
btv_cost_total_usd $cost
btv_cost_requests_total $requests
btv_cost_avg_per_request $avg
EOF

  # Lock metrics
  IFS='|' read -r active orphan <<< "$(calculate_lock_metrics)"
  cat >> "$METRICS_FILE" <<EOF
btv_locks_active $active
btv_locks_orphan $orphan
EOF

  echo "✅ Métricas exportadas para $METRICS_FILE"
}

###############################################################################
# Execução
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  generate_prometheus_metrics
fi