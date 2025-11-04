#!/bin/bash
# Validar plano

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PLAN_ID|PLAN_FILE>" >&2
  exit 1
fi

INPUT="$1"
PLAN_FILE=""

if [[ -f "$INPUT" ]]; then
  PLAN_FILE="$INPUT"
else
  PLAN_FILE=".buildtovalue/plans/active/${INPUT}.json"
fi

if [[ ! -f "$PLAN_FILE" ]]; then
  echo "❌ Plan file not found: $PLAN_FILE" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required to validate plans" >&2
  exit 1
fi

if ! jq empty "$PLAN_FILE" >/dev/null 2>&1; then
  echo "❌ Invalid JSON" >&2
  exit 1
fi

SPEC_BASE=".buildtovalue/specifications"
CONTRACTS=$(jq -r '.buildtovalue_plan.prerequisites.contracts[]?' "$PLAN_FILE")
for contract in $CONTRACTS; do
  if [[ -f "$contract" ]]; then
    continue
  fi

  if [[ ! -f "$SPEC_BASE/$contract" ]]; then
    echo "❌ Missing contract: $contract" >&2
    exit 1
  fi
done

PERSONAS_DIR=".buildtovalue/squad/personas"
IAS=$(jq -r '.buildtovalue_plan.execution_sequence[] | .primary_ia // empty' "$PLAN_FILE")
SUPPORT_IAS=$(jq -r '.buildtovalue_plan.execution_sequence[] | (.support_ias[]?)' "$PLAN_FILE")
ALL_IAS=$(printf "%s\n%s\n" "$IAS" "$SUPPORT_IAS" | sort -u | sed '/^$/d')

if [[ -n "$ALL_IAS" ]]; then
  if [[ -d "$PERSONAS_DIR" ]]; then
    while IFS= read -r ia; do
      if [[ ! -f "$PERSONAS_DIR/${ia}.yaml" ]]; then
        echo "❌ Unknown IA: $ia" >&2
        exit 1
      fi
    done <<<"$ALL_IAS"
  else
    echo "⚠️  Personas directory not found. Skipping IA validation." >&2
  fi
fi

if [[ -f .buildtovalue/config/governance.yaml ]] && command -v yq >/dev/null 2>&1; then
  MAX_COST=$(yq eval '.planning_policy.budget_limits.max_ia_cost_per_plan' .buildtovalue/config/governance.yaml 2>/dev/null || echo "")
  MAX_DURATION=$(yq eval '.planning_policy.budget_limits.max_duration_hours' .buildtovalue/config/governance.yaml 2>/dev/null || echo "")
  MAX_CALLS=$(yq eval '.planning_policy.budget_limits.max_ia_calls' .buildtovalue/config/governance.yaml 2>/dev/null || echo "")

  PLAN_COST=$(jq -r '.buildtovalue_plan.budget.estimated_ia_cost // ""' "$PLAN_FILE" | tr -d '$')
  PLAN_DURATION=$(jq -r '.buildtovalue_plan.budget.estimated_duration // ""' "$PLAN_FILE" | tr -dc '0-9.')
  PLAN_CALLS=$(jq -r '.buildtovalue_plan.budget.max_ia_calls // 0' "$PLAN_FILE")

  if [[ -n "$MAX_COST" && -n "$PLAN_COST" ]]; then
    awk "BEGIN {exit !($PLAN_COST <= $MAX_COST)}" || {
      echo "❌ Plan exceeds max IA cost (${PLAN_COST} > ${MAX_COST})" >&2
      exit 1
    }
  fi

  if [[ -n "$MAX_DURATION" && -n "$PLAN_DURATION" ]]; then
    awk "BEGIN {exit !($PLAN_DURATION <= $MAX_DURATION)}" || {
      echo "❌ Plan exceeds max duration (${PLAN_DURATION}h > ${MAX_DURATION}h)" >&2
      exit 1
    }
  fi

  if [[ -n "$MAX_CALLS" ]]; then
    if (( PLAN_CALLS > MAX_CALLS )); then
      echo "❌ Plan exceeds max IA calls (${PLAN_CALLS} > ${MAX_CALLS})" >&2
      exit 1
    fi
  fi
fi

echo "✅ Plan validated"
