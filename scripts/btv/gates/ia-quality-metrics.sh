#!/bin/bash
# Calcular métricas de qualidade da IA

set -euo pipefail

OVERRIDE_RATE="N/A"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GENERATED_COMMITS=$(git log --all --pretty=format: --name-only | grep -E '(generated|ai-output)' || true)
  TOTAL_COMMITS=$(git log --all --pretty=oneline | wc -l | tr -d ' ')
  if [[ -n "$GENERATED_COMMITS" && $TOTAL_COMMITS -gt 0 ]]; then
    COUNT=$(echo "$GENERATED_COMMITS" | sort -u | wc -l | tr -d ' ')
    OVERRIDE_RATE=$((COUNT * 100 / TOTAL_COMMITS))%
  else
    OVERRIDE_RATE="0%"
  fi
fi

FLAKY_TESTS="N/A"
if [[ -x ./scripts/testing/detect-flaky-tests.sh ]]; then
  FLAKY_TESTS=$(./scripts/testing/detect-flaky-tests.sh | wc -l | tr -d ' ')
else
  FLAKY_TESTS=0
fi

TOKEN_EFFICIENCY="N/A"
if [[ -f .buildtovalue/ledger/metrics.json ]] && command -v jq >/dev/null 2>&1; then
  TOKEN_EFFICIENCY=$(jq -r '.metrics.tokens_per_success // "N/A"' .buildtovalue/ledger/metrics.json)
fi

echo "📊 IA Quality Metrics:"
echo "Override Rate: ${OVERRIDE_RATE}"
echo "Flaky Tests: ${FLAKY_TESTS}"
echo "Token Efficiency: ${TOKEN_EFFICIENCY}"
