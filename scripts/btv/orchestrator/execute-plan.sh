#!/bin/bash
# Executar plano aprovado

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PLAN_ID|PLAN_FILE>" >&2
  exit 1
fi

PLAN_ARG="$1"

if [[ -f "$PLAN_ARG" ]]; then
  PLAN_FILE="$PLAN_ARG"
else
  PLAN_FILE=".buildtovalue/plans/active/${PLAN_ARG}.json"
fi

if [[ ! -f "$PLAN_FILE" ]]; then
  echo "❌ Plan file not found: $PLAN_FILE" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required to execute plans" >&2
  exit 1
fi

STATUS=$(jq -r '.buildtovalue_plan.status // "draft"' "$PLAN_FILE")
if [[ "$STATUS" != "approved" ]]; then
  echo "❌ Plan not approved" >&2
  exit 1
fi

PLAN_ID=$(jq -r '.buildtovalue_plan.id' "$PLAN_FILE")
PHASES=$(jq -c '.buildtovalue_plan.execution_sequence[]' "$PLAN_FILE")

while IFS= read -r phase; do
  [[ -z "$phase" ]] && continue
  PHASE_NAME=$(jq -r '.phase' <<<"$phase")
  PRIMARY_IA=$(jq -r '.primary_ia' <<<"$phase")

  echo "🚀 Executing phase: ${PHASE_NAME} with ${PRIMARY_IA}"

  if [[ -x ./scripts/orchestrator/activate-ia.sh ]]; then
    ./scripts/orchestrator/activate-ia.sh "$PRIMARY_IA" \
      --context="$PHASE_NAME" \
      --plan="$PLAN_ID"
  else
    echo "⚠️  activate-ia.sh not found. Log this phase manually." >&2
  fi

  # TODO: Implement deliverable validation per phase requirements

done <<<"$PHASES"

mkdir -p .buildtovalue/plans/completed
mv "$PLAN_FILE" ".buildtovalue/plans/completed/$(basename "$PLAN_FILE")"

echo "✅ Plan execution completed"
