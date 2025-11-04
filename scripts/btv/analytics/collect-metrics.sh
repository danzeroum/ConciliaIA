#!/usr/bin/env bash
# 📈 Coleta métricas reais de decisões e SLOs
set -e
PROM_URL=${PROM_URL:-"http://localhost:9090/api/v1/query"}
OUTPUT=".buildtovalue/reports/metrics-$(date +%Y%m%d).json"

echo "📊 Coletando métricas de valor (7 dias)..."
curl -s "${PROM_URL}?query=buildtovalue_decisions_total" |
 jq '.data.result[]?' > /tmp/prom_metrics.json || true

TOTAL=$(grep -c '"metric"' /tmp/prom_metrics.json 2>/dev/null || true)
TOTAL=${TOTAL:-0}
AVG_CONF=$(grep -Eo '"confidence":[0-9.]+' .buildtovalue/logs/*.json 2>/dev/null |
  awk -F: '{sum+=$2;count++}END{if(count>0)print sum/count;else print 0}')
FAIL=$(grep -c '"outcome":"failed"' .buildtovalue/logs/*.json 2>/dev/null || true)
FAIL=${FAIL:-0}
SUCCESS=$(awk -v t=$TOTAL -v f=$FAIL 'BEGIN{if(t>0)print (t-f)/t;else print 0}')

cat <<JSON > "$OUTPUT"
{
 "timestamp": "$(date -Iseconds)",
 "total_decisions": $TOTAL,
 "avg_confidence": $AVG_CONF,
 "failures": $FAIL,
 "success_rate": $SUCCESS
}
JSON
echo "✅ Métricas geradas em $OUTPUT"
