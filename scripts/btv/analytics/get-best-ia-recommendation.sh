#!/bin/bash
# BuildToValue v7.1 - Recomendação de melhor IA

PERSONA=${1:-"ia-developer"}
ANALYTICS_FILE=".buildtovalue/analytics/ia-performance.jsonl"

if [ ! -f "$ANALYTICS_FILE" ]; then
  echo "claude"
  exit 0
fi

BEST_IA=$(jq -r --arg persona "$PERSONA" '
  select(.persona == $persona) | .ia
' "$ANALYTICS_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')

echo "${BEST_IA:-claude}"
