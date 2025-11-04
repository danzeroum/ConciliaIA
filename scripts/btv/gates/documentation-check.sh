#!/bin/bash
# BuildToValue v7.1 - Documentation Gate

set -e

echo "📚 Checking required documentation..."

PLAN_ID=$(git log -1 --pretty=%B | grep -oP 'PLAN-\d+-\w+' || echo "")

if [ -z "$PLAN_ID" ]; then
  REQUIRED_DOCS=("README.md")
else
  PLAN_FILE=".buildtovalue/plans/active/${PLAN_ID}.json"
  [ ! -f "$PLAN_FILE" ] && PLAN_FILE=".buildtovalue/plans/completed/${PLAN_ID}.json"

  if [ -f "$PLAN_FILE" ]; then
    mapfile -t REQUIRED_DOCS < <(jq -r '
      .buildtovalue_plan.execution_sequence[] |
      select(.phase == "documentation" or .phase == "implementation") |
      .deliverables[] |
      select(test("\\.md$"))
    ' "$PLAN_FILE" 2>/dev/null)
  else
    REQUIRED_DOCS=("README.md")
  fi
fi

if [ ${#REQUIRED_DOCS[@]} -eq 0 ]; then
  REQUIRED_DOCS=("README.md")
fi

MISSING=()
for doc in "${REQUIRED_DOCS[@]}"; do
  if [ -n "$doc" ] && [ ! -f "$doc" ]; then
    MISSING+=("$doc")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "❌ Missing documentation:"
  for doc in "${MISSING[@]}"; do
    echo "   - $doc"
  done
  exit 1
fi

echo "✅ Documentation check passed"
exit 0
