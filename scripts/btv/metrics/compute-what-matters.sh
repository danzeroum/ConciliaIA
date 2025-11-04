#!/usr/bin/env bash
set -euo pipefail

# --- BuildToValue v7.1 Resilience Fallback ---
if ! docker ps --format "{{.Names}}" | grep -q "^buildtovalue-postgres$"; then
  echo "⚠️  Container buildtovalue-postgres não encontrado — iniciando localmente..."
  docker run -d --name buildtovalue-postgres \
    -e POSTGRES_USER=btv_user -e POSTGRES_PASSWORD=changeme123 -e POSTGRES_DB=buildtovalue \
    -p 5432:5432 postgres:16
  sleep 10
fi

# ==========================================
# NOTAS DE COMPATIBILIDADE
# ==========================================
# Este script usa GNU date (date -d, date -Iseconds) que não existe no BSD/macOS.
# Como o CI/CD roda em Ubuntu (GitHub Actions runners), isso é aceitável.
#
# Para uso local em macOS, instale coreutils:
#   brew install coreutils
#   export PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
# ==========================================

OUT=".buildtovalue/reports/what-matters.json"
PROM_URL="${PROMETHEUS_URL:-http://localhost:9090}"
WINDOW_DAYS="${WINDOW_DAYS:-7}"
LEDGER="ledger/traceability-ledger.jsonl"

mkdir -p "$(dirname "$OUT")"

log_metric() { echo "[what-matters] $1"; }

# ==========================================
# 1. DEPLOYMENT FREQUENCY (deploys/week)
# ==========================================
log_metric "Calculando deployment frequency..."

# Método 1: Git tags
DEP_FREQ_GIT=$(git tag --list 'release-*' --sort=-taggerdate | \
  xargs -I{} git log -1 --format='%ct' {} 2>/dev/null | \
  awk -v now="$(date +%s)" -v window="$((WINDOW_DAYS * 86400))" \
    '$1 > (now - window)' | wc -l | tr -d ' ')

# Método 2: CI/CD ledger (se disponível)
DEP_FREQ_LEDGER=0
if [ -f "$LEDGER" ]; then
  DEP_FREQ_LEDGER=$(jq -r --arg w "$WINDOW_DAYS" '
    select((.task // "") | contains("deploy")) |
    select(.outcome == "success") |
    select((.timestamp | fromdateiso8601) > (now - ($w | tonumber * 86400)))
  ' "$LEDGER" 2>/dev/null | wc -l | tr -d ' ')
fi

# Método 3: Prometheus (se disponível)
DEP_FREQ_PROM=0
if command -v curl >/dev/null && curl -sf "$PROM_URL/-/healthy" >/dev/null 2>&1; then
  DEP_FREQ_PROM=$(curl -sf "$PROM_URL/api/v1/query" \
    --data-urlencode "query=sum(increase(deployment_total{env=\"production\"}[${WINDOW_DAYS}d]))" | \
    jq -r '.data.result[0].value[1] // 0' 2>/dev/null || echo 0)
fi

# Usar o máximo dos 3 métodos (mais confiável)
DEP_FREQ=$(echo "$DEP_FREQ_GIT $DEP_FREQ_LEDGER $DEP_FREQ_PROM" | awk '{print ($1>$2)?($1>$3?$1:$3):($2>$3?$2:$3)}')

# ==========================================
# 2. LEAD TIME FOR CHANGES (mediana, em minutos)
# ==========================================
log_metric "Calculando lead time..."

# Git: tempo entre primeiro commit de PR e merge
LEAD_TIMES=$(git log --since="${WINDOW_DAYS} days ago" --grep='Merge pull request' --pretty='%ct %s' | \
  awk '{
    merge_time=$1;
    if (match($0, /#[0-9]+/)) {
      pr=substr($0, RSTART+1, RLENGTH-1);
      # Buscar primeiro commit do PR (heurística)
      cmd="git log --all --grep=\"#"pr"\" --reverse --pretty=\"%ct\" 2>/dev/null | head -1";
      cmd | getline first_commit;
      close(cmd);
      if (first_commit != "") {
        lead_sec=merge_time - first_commit;
        if (lead_sec > 0) print lead_sec / 60;  # Converter para minutos
      }
    }
  }' | sort -n)

LEAD_MED=$(echo "$LEAD_TIMES" | awk '{a[NR]=$1} END {print (NR%2==1) ? a[(NR+1)/2] : (a[NR/2] + a[NR/2+1])/2}')
LEAD_MED=${LEAD_MED:-0}

# ==========================================
# 3. CHANGE FAILURE RATE (%)
# ==========================================
log_metric "Calculando change failure rate..."

TOTAL_CHANGES=$(git log --since="${WINDOW_DAYS} days ago" --grep='Merge pull request' --oneline | wc -l | tr -d ' ')
FAILED_CHANGES=$(git log --since="${WINDOW_DAYS} days ago" --grep='revert\|hotfix\|rollback' --oneline | wc -l | tr -d ' ')

CFR=$(awk -v f="$FAILED_CHANGES" -v t="$TOTAL_CHANGES" 'BEGIN{
  if (t == 0) print 0; 
  else printf "%.4f", (f / t)
}')

# ==========================================
# 4. MTTR (Mean Time To Recovery, em minutos)
# ==========================================
log_metric "Calculando MTTR..."

# Método 1: Ledger de incidentes (formato: incident_start → incident_resolved)
MTTR=0
if [ -f "$LEDGER" ]; then
  # Buscar pares de eventos incident:start e incident:resolved
  INCIDENT_PAIRS=$(jq -r --arg w "$WINDOW_DAYS" '
    select((.task // "") | contains("incident")) |
    select((.timestamp | fromdateiso8601) > (now - ($w | tonumber * 86400))) |
    "\(.id)|\(.task)|\(.timestamp)"
  ' "$LEDGER" 2>/dev/null | \
  awk -F'|' '
    /incident:start/ { start[$1]=$3 }
    /incident:resolved/ {
      if (start[$1]) {
        # Calcular delta em minutos
        cmd="date -d "$3" +%s";
        cmd | getline resolved_ts;
        close(cmd);
        cmd="date -d "start[$1]" +%s";
        cmd | getline start_ts;
        close(cmd);
        print (resolved_ts - start_ts) / 60;
      }
    }
  ')
  
  if [ -n "$INCIDENT_PAIRS" ]; then
    MTTR=$(echo "$INCIDENT_PAIRS" | awk '{s+=$1; n++} END{if(n>0) print s/n; else print 0}')
  fi
fi

# Método 2: Prometheus (alertas resolvidos)
if [ "$MTTR" = "0" ] && command -v curl >/dev/null && curl -sf "$PROM_URL/-/healthy" >/dev/null 2>&1; then
  MTTR=$(curl -sf "$PROM_URL/api/v1/query" \
    --data-urlencode "query=avg_over_time(alert_resolution_time_minutes[${WINDOW_DAYS}d])" | \
    jq -r '.data.result[0].value[1] // 0' 2>/dev/null || echo 0)
fi

# ==========================================
# 5. FLAKY TEST RATE (%)
# ==========================================
log_metric "Calculando flaky test rate..."

FLAKY_EVENTS=0
TOTAL_TESTS=1  # Evitar divisão por zero

# Método 1: JUnit XML
if [ -f ".buildtovalue/reports/junit.xml" ]; then
  FLAKY_EVENTS=$(grep -oiE 'flaky|rerun' .buildtovalue/reports/junit.xml | wc -l | tr -d ' ')
  TOTAL_TESTS=$(grep -c '<testcase' .buildtovalue/reports/junit.xml | tr -d ' ')
fi

# Método 2: pytest-rerunfailures log
if [ -f ".buildtovalue/reports/pytest-rerun.log" ]; then
  FLAKY_FROM_PYTEST=$(grep -c 'RERUN' .buildtovalue/reports/pytest-rerun.log || echo 0)
  FLAKY_EVENTS=$((FLAKY_EVENTS + FLAKY_FROM_PYTEST))
fi

FLAKY_RATE=$(awk -v f="$FLAKY_EVENTS" -v t="$TOTAL_TESTS" 'BEGIN{printf "%.4f", (t>0 ? f/t : 0)}')

# ==========================================
# 6. AI REWORK RATIO (% código reescrito)
# ==========================================
log_metric "Calculando AI rework ratio..."

# Heurística: comparar diff de PRs gerados por IA vs. PR final mergeado
# Requer tagging no ledger: ia_generated=true
AI_PR_DIFFS=$(jq -r --arg w "$WINDOW_DAYS" '
  select((.task // "") | contains("PR")) |
  select(.ia_generated == true) |
  select((.timestamp | fromdateiso8601) > (now - ($w | tonumber * 86400))) |
  .artifact_path
' "$LEDGER" 2>/dev/null || true)

REWORK_RATIO=0
if [ -n "$AI_PR_DIFFS" ]; then
  TOTAL_AI_LINES=0
  CHANGED_LINES=0
  
  while IFS= read -r pr_path; do
    if [ -f "$pr_path" ]; then
      # Contar linhas da versão original IA
      AI_LINES=$(wc -l < "$pr_path" | tr -d ' ')
      TOTAL_AI_LINES=$((TOTAL_AI_LINES + AI_LINES))
      
      # Contar linhas modificadas em commits subsequentes
      MODS=$(git log --since="${WINDOW_DAYS} days ago" --pretty="" --numstat -- "$pr_path" | \
        awk '{add+=$1; del+=$2} END{print add+del}')
      CHANGED_LINES=$((CHANGED_LINES + ${MODS:-0}))
    fi
  done <<< "$AI_PR_DIFFS"
  
  [ "$TOTAL_AI_LINES" -gt 0 ] && \
    REWORK_RATIO=$(awk -v c="$CHANGED_LINES" -v t="$TOTAL_AI_LINES" 'BEGIN{printf "%.4f", c/t}')
fi

# ==========================================
# CALCULAR STATUS ANTES DO HERE-DOC (FIX 1)
# ==========================================

DF_STATUS=$([ "$DEP_FREQ" -ge 14 ] && echo "PASS" || echo "FAIL")
LEAD_STATUS=$(awk -v l="$LEAD_MED" 'BEGIN{print (l<=360?"PASS":"FAIL")}')
CFR_STATUS=$(awk -v c="$CFR" 'BEGIN{print (c<=0.15?"PASS":"FAIL")}')
MTTR_STATUS=$(awk -v m="$MTTR" 'BEGIN{print (m<=60?"PASS":"FAIL")}')
FLAKY_STATUS=$(awk -v f="$FLAKY_RATE" 'BEGIN{print (f<=0.02?"PASS":"FAIL")}')
REWORK_STATUS=$(awk -v r="$REWORK_RATIO" 'BEGIN{print (r<=0.15?"PASS":"FAIL")}')

# Contar falhas
FAILS=0
for s in "$DF_STATUS" "$LEAD_STATUS" "$CFR_STATUS" "$MTTR_STATUS" "$FLAKY_STATUS" "$REWORK_STATUS"; do
  [ "$s" = "FAIL" ] && FAILS=$((FAILS + 1))
done

# Status geral
OVERALL_STATUS=$([ $FAILS -eq 0 ] && echo "PASS" || echo "FAIL")

# ==========================================
# GERAR RELATÓRIO JSON
# ==========================================
cat > "$OUT" <<JSON
{
  "generated_at": "$(date -Iseconds)",
  "window_days": $WINDOW_DAYS,
  "dora_metrics": {
    "deployment_frequency": {
      "name": "Deployment Frequency",
      "description": "How often code is deployed to production",
      "value": $DEP_FREQ,
      "unit": "deploys/${WINDOW_DAYS}d",
      "sources": ["git_tags", "ledger", "prometheus"],
      "target": 14,
      "status": "$DF_STATUS",
      "category": "DORA",
      "dora_category": "Throughput"
    },
    "lead_time_for_changes": {
      "name": "Lead Time for Changes",
      "description": "Time from commit to production",
      "value": $LEAD_MED,
      "unit": "minutes",
      "target": 360,
      "status": "$LEAD_STATUS",
      "category": "DORA",
      "dora_category": "Speed"
    },
    "change_failure_rate": {
      "name": "Change Failure Rate",
      "description": "Percentage of deployments causing failures",
      "value": $CFR,
      "unit": "ratio",
      "target": 0.15,
      "status": "$CFR_STATUS",
      "category": "DORA",
      "dora_category": "Stability"
    },
    "mean_time_to_recovery": {
      "name": "Mean Time To Recovery",
      "description": "Average time to recover from incidents",
      "value": $MTTR,
      "unit": "minutes",
      "sources": ["ledger", "prometheus"],
      "target": 60,
      "status": "$MTTR_STATUS",
      "category": "DORA",
      "dora_category": "Reliability"
    }
  },
  "quality_metrics": {
    "flaky_test_rate": {
      "name": "Flaky Test Rate",
      "description": "Percentage of tests that fail intermittently",
      "value": $FLAKY_RATE,
      "unit": "ratio",
      "flaky_count": $FLAKY_EVENTS,
      "total_tests": $TOTAL_TESTS,
      "target": 0.02,
      "status": "$FLAKY_STATUS",
      "category": "Quality"
    },
    "ai_rework_ratio": {
      "name": "AI Rework Ratio",
      "description": "Percentage of AI-generated code that is rewritten",
      "value": $REWORK_RATIO,
      "unit": "ratio",
      "target": 0.15,
      "status": "$REWORK_STATUS",
      "category": "Quality"
    }
  },
  "overall_status": "$OVERALL_STATUS",
  "metadata": {
    "buildtovalue_version": "7.1.0",
    "schema_version": "1.0",
    "computed_by": "scripts/metrics/compute-what-matters.sh"
  }
}
JSON

log_metric "✅ Relatório gerado em $OUT"

# Exibir resumo visual
echo ""
echo "📊 RESUMO - What Matters Metrics"
echo "================================="
jq -r '
  "🚀 Deployment Frequency: \(.dora_metrics.deployment_frequency.value) \(.dora_metrics.deployment_frequency.status)",
  "⏱️  Lead Time: \(.dora_metrics.lead_time_for_changes.value) min \(.dora_metrics.lead_time_for_changes.status)",
  "❌ Change Failure Rate: \(.dora_metrics.change_failure_rate.value * 100 | floor)% \(.dora_metrics.change_failure_rate.status)",
  "🔧 MTTR: \(.dora_metrics.mean_time_to_recovery.value) min \(.dora_metrics.mean_time_to_recovery.status)",
  "🧪 Flaky Test Rate: \(.quality_metrics.flaky_test_rate.value * 100 | floor)% \(.quality_metrics.flaky_test_rate.status)",
  "🤖 AI Rework Ratio: \(.quality_metrics.ai_rework_ratio.value * 100 | floor)% \(.quality_metrics.ai_rework_ratio.status)"
' "$OUT"
echo "================================="
echo ""

# Notificar via Slack se algum falhou (se SLACK_WEBHOOK_URL configurado)
if [ "$OVERALL_STATUS" = "FAIL" ] && [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
  FAILED_METRICS=$(jq -r '
    [
      (.dora_metrics | to_entries[] | 
        select(.value.status == "FAIL") | .key),
      (.quality_metrics | to_entries[] | 
        select(.value.status == "FAIL") | .key)
    ] |
    join(", ")
  ' "$OUT")
  
  # Usar curl silencioso e redirecionar erros para /dev/null (FIX 3)
  curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{
      \"text\": \"⚠️ What Matters Alert\",
      \"attachments\": [{
        \"color\": \"danger\",
        \"title\": \"Métricas abaixo do target\",
        \"text\": \"Falhas em: $FAILED_METRICS\",
        \"footer\": \"BuildToValue Metrics\",
        \"ts\": $(date +%s)
      }]
    }" 2>/dev/null || {
      # Falha silenciosa - não expor webhook em logs de erro
      log_metric "⚠️  Falha ao notificar Slack (verifique SLACK_WEBHOOK_URL)"
    }
fi

# Registrar no ledger
if [ -f "scripts/ledger/auto-log-decision.sh" ]; then
  ./scripts/ledger/auto-log-decision.sh \
    "metrics-collector" \
    "What Matters metrics computed: $OVERALL_STATUS" \
    "$(echo $OVERALL_STATUS | tr '[:upper:]' '[:lower:]')" \
    0.92
fi
