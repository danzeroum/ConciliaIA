#!/usr/bin/env bash
set -euo pipefail

REPORT=".buildtovalue/reports/what-matters.json"
STRICT_MODE="${STRICT_MODE:-false}"
NOTIFY="${NOTIFY:-true}"

# Gerar relatório se não existir
if [ ! -f "$REPORT" ]; then
  echo "ℹ️  Relatório não existe. Gerando..."
  scripts/metrics/compute-what-matters.sh || {
    echo "❌ Falha ao gerar relatório"
    exit 1
  }
fi

# Validar JSON
if ! jq empty "$REPORT" 2>/dev/null; then
  echo "❌ Relatório corrompido: $REPORT"
  exit 1
fi

# Extrair status geral
OVERALL=$(jq -r '.overall_status' "$REPORT")
WINDOW=$(jq -r '.window_days' "$REPORT")

echo "📊 What Matters Gate - Janela: ${WINDOW}d"
echo "========================================"

# Exibir métricas com status visual
jq -r '
  def status_icon: if . == "PASS" then "✅" else "❌" end;
  
  "DORA Metrics:",
  "  Deployment Frequency: \(.dora_metrics.deployment_frequency.value) deploys | Target: ≥\(.dora_metrics.deployment_frequency.target) | \(.dora_metrics.deployment_frequency.status | status_icon)",
  "  Lead Time: \(.dora_metrics.lead_time_for_changes.value) min | Target: ≤\(.dora_metrics.lead_time_for_changes.target) min | \(.dora_metrics.lead_time_for_changes.status | status_icon)",
  "  Change Failure Rate: \((.dora_metrics.change_failure_rate.value * 100) | floor)% | Target: ≤15% | \(.dora_metrics.change_failure_rate.status | status_icon)",
  "  MTTR: \(.dora_metrics.mean_time_to_recovery.value) min | Target: ≤\(.dora_metrics.mean_time_to_recovery.target) min | \(.dora_metrics.mean_time_to_recovery.status | status_icon)",
  "",
  "Quality Metrics:",
  "  Flaky Test Rate: \((.quality_metrics.flaky_test_rate.value * 100) | floor)% | Target: ≤2% | \(.quality_metrics.flaky_test_rate.status | status_icon)",
  "  AI Rework Ratio: \((.quality_metrics.ai_rework_ratio.value * 100) | floor)% | Target: ≤15% | \(.quality_metrics.ai_rework_ratio.status | status_icon)"
' "$REPORT"

echo "========================================"

# Verificar modo de operação
if [ "$OVERALL" = "PASS" ]; then
  echo "✅ What-Matters gate APROVADO"
  exit 0
else
  FAIL_COUNT=$(jq -r '
    [
      (.dora_metrics | to_entries[] | select(.value.status == "FAIL")),
      (.quality_metrics | to_entries[] | select(.value.status == "FAIL"))
    ] | length
  ' "$REPORT")
  
  echo "⚠️  What-Matters gate com $FAIL_COUNT falha(s)"
  
  # Gerar relatório detalhado de falhas (FIX 4)
  FAILED_DETAILS=$(jq -r '
    [
      (.dora_metrics | to_entries[] | 
        {category: "DORA", metric: .key, data: .value}),
      (.quality_metrics | to_entries[] | 
        {category: "Quality", metric: .key, data: .value})
    ] |
    map(select(.data.status == "FAIL")) |
    map("- [\(.category)] \(.metric): atual=\(.data.value) \(.data.unit), target=\(.data.target) \(.data.unit)") |
    join("\n")
  ' "$REPORT")
  
  echo ""
  echo "Detalhes das falhas:"
  echo "$FAILED_DETAILS"
  echo ""
  
  # Sugestões de ação
  echo "💡 Ações recomendadas:"
  jq -r '
    if (.dora_metrics.deployment_frequency.status == "FAIL") then
      "  • Aumentar frequência de deploys: automatizar CI/CD, reduzir batch size"
    else empty end,
    
    if (.dora_metrics.lead_time_for_changes.status == "FAIL") then
      "  • Reduzir lead time: PRs menores, revisão mais rápida, automation"
    else empty end,
    
    if (.dora_metrics.change_failure_rate.status == "FAIL") then
      "  • Melhorar qualidade: aumentar cobertura de testes, pair programming"
    else empty end,
    
    if (.dora_metrics.mean_time_to_recovery.status == "FAIL") then
      "  • Acelerar recuperação: melhorar monitoramento, automatizar rollback"
    else empty end,
    
    if (.quality_metrics.flaky_test_rate.status == "FAIL") then
      "  • Corrigir testes flaky: quarentena automática, investigar root cause"
    else empty end,
    
    if (.quality_metrics.ai_rework_ratio.status == "FAIL") then
      "  • Melhorar qualidade IA: refinar prompts, validação pré-merge"
    else empty end
  ' "$REPORT"
  
  # Notificar se configurado (FIX 3 - sem ecoar webhook)
  if [ "$NOTIFY" = "true" ] && [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    FAILED_METRICS=$(jq -r '
      [
        (.dora_metrics | to_entries[] | 
          select(.value.status == "FAIL") | .key),
        (.quality_metrics | to_entries[] | 
          select(.value.status == "FAIL") | .key)
      ] |
      join(", ")
    ' "$REPORT")
    
    curl -X POST "$SLACK_WEBHOOK_URL" \
      -H 'Content-Type: application/json' \
      -d "{
        \"text\": \"⚠️ What Matters Gate Failed\",
        \"attachments\": [{
          \"color\": \"warning\",
          \"title\": \"$FAIL_COUNT métrica(s) abaixo do target\",
          \"text\": \"$(echo "$FAILED_DETAILS" | sed 's/"/\\"/g')\",
          \"footer\": \"BuildToValue Quality Gates\",
          \"ts\": $(date +%s)
        }]
      }" 2>/dev/null || {
        echo "⚠️  Falha ao notificar Slack (verifique SLACK_WEBHOOK_URL)"
      }
  fi
  
  # Em modo estrito, falhar o gate
  if [ "$STRICT_MODE" = "true" ]; then
    echo ""
    echo "❌ Gate REPROVADO (STRICT_MODE=true)"
    exit 1
  else
    echo ""
    echo "⚠️  Gate com AVISOS (STRICT_MODE=false, passando)"
    exit 0
  fi
fi
