#!/usr/bin/env bash
set -euo pipefail

REPORT=".buildtovalue/reports/what-matters.json"
OUTPUT="${1:--}"  # stdout por padrão

if [ "$OUTPUT" = "-" ]; then
  OUTPUT=/dev/stdout
fi

[ ! -f "$REPORT" ] && {
  echo "# ERROR: Report not found at $REPORT" >&2
  exit 1
}

# Converter JSON para formato Prometheus text
{
  echo "# HELP btv_deployment_frequency Number of deployments in the window"
  echo "# TYPE btv_deployment_frequency gauge"
  jq -r '.dora_metrics.deployment_frequency.value' "$REPORT" | \
    awk '{printf "btv_deployment_frequency %d\n", $1}'
  
  echo "# HELP btv_lead_time_minutes Lead time for changes in minutes"
  echo "# TYPE btv_lead_time_minutes gauge"
  jq -r '.dora_metrics.lead_time_for_changes.value' "$REPORT" | \
    awk '{printf "btv_lead_time_minutes %.2f\n", $1}'
  
  echo "# HELP btv_change_failure_rate Change failure rate (0.0-1.0)"
  echo "# TYPE btv_change_failure_rate gauge"
  jq -r '.dora_metrics.change_failure_rate.value' "$REPORT" | \
    awk '{printf "btv_change_failure_rate %.4f\n", $1}'
  
  echo "# HELP btv_mttr_minutes Mean time to recovery in minutes"
  echo "# TYPE btv_mttr_minutes gauge"
  jq -r '.dora_metrics.mean_time_to_recovery.value' "$REPORT" | \
    awk '{printf "btv_mttr_minutes %.2f\n", $1}'
  
  echo "# HELP btv_flaky_test_rate Flaky test rate (0.0-1.0)"
  echo "# TYPE btv_flaky_test_rate gauge"
  jq -r '.quality_metrics.flaky_test_rate.value' "$REPORT" | \
    awk '{printf "btv_flaky_test_rate %.4f\n", $1}'
  
  echo "# HELP btv_ai_rework_ratio AI rework ratio (0.0-1.0)"
  echo "# TYPE btv_ai_rework_ratio gauge"
  jq -r '.quality_metrics.ai_rework_ratio.value' "$REPORT" | \
    awk '{printf "btv_ai_rework_ratio %.4f\n", $1}'
  
  # Status geral (1=PASS, 0=FAIL)
  echo "# HELP btv_overall_status Overall metrics status (1=PASS, 0=FAIL)"
  echo "# TYPE btv_overall_status gauge"
  jq -r '.overall_status' "$REPORT" | \
    awk '{print ($1=="PASS"?"btv_overall_status 1":"btv_overall_status 0")}'
} > "$OUTPUT"

[ "$OUTPUT" != "/dev/stdout" ] && echo "✅ Prometheus metrics exported to $OUTPUT"
