#!/usr/bin/env bash
# 💹 Calcula ROI com base nas métricas reais
set -e
METRICS_FILE=${1:-.buildtovalue/reports/metrics-$(date +%Y%m%d).json}
OUT=".buildtovalue/reports/roi-$(date +%Y%m%d).json"
COST_PER_DEC=${COST_PER_DECISION:-0.05}
REV_PER_DEC=${REVENUE_PER_DECISION:-0.25}

TOTAL=$(jq '.total_decisions' "$METRICS_FILE")
SUCCESS=$(jq '.success_rate' "$METRICS_FILE")
GAINS=$(awk -v t=$TOTAL -v s=$SUCCESS -v r=$REV_PER_DEC 'BEGIN{print t*s*r}')
COSTS=$(awk -v t=$TOTAL -v c=$COST_PER_DEC 'BEGIN{print t*c}')
ROI=$(awk -v g=$GAINS -v c=$COSTS 'BEGIN{if(c>0)print (g-c)/c;else print 0}')

cat <<JSON > "$OUT"
{
 "timestamp": "$(date -Iseconds)",
 "total_decisions": $TOTAL,
 "success_rate": $SUCCESS,
 "gains_usd": $GAINS,
 "costs_usd": $COSTS,
 "roi_ratio": $ROI
}
JSON
echo "✅ ROI calculado → $OUT"
