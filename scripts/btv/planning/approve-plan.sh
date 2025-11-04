#!/bin/bash
# Aprovar plano

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PLAN_ID|PLAN_FILE> --reviewer EMAIL [--type TYPE]" >&2
  exit 1
fi

PLAN_ARG="$1"
shift

REVIEWER=""
REVIEW_TYPE="architecture-review"

while [[ $# -gt 0 ]]; do
  case $1 in
    --reviewer)
      REVIEWER="$2"
      shift 2
      ;;
    --reviewer=*)
      REVIEWER="${1#*=}"
      shift
      ;;
    --type)
      REVIEW_TYPE="$2"
      shift 2
      ;;
    --type=*)
      REVIEW_TYPE="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REVIEWER" ]]; then
  echo "❌ Reviewer email is required" >&2
  exit 1
fi

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
  echo "❌ jq is required to approve plans" >&2
  exit 1
fi

APPROVED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

TMP_FILE="${PLAN_FILE}.tmp"

jq --arg type "$REVIEW_TYPE" \
   --arg reviewer "$REVIEWER" \
   --arg approved_at "$APPROVED_AT" \
   '.buildtovalue_plan.prerequisites.approvals += [{type: $type, reviewer: $reviewer, approved_at: $approved_at}]' \
   "$PLAN_FILE" > "$TMP_FILE"

mv "$TMP_FILE" "$PLAN_FILE"

STATUS_MSG="⏳ Plan partially approved"

if [[ -f .buildtovalue/config/governance.yaml ]] && command -v yq >/dev/null 2>&1; then
  REQUIRED=$(yq eval '.planning_policy.required_approvals[]' .buildtovalue/config/governance.yaml 2>/dev/null || true)
  if [[ -n "$REQUIRED" ]]; then
    CURRENT=$(jq -r '.buildtovalue_plan.prerequisites.approvals[].type' "$PLAN_FILE" | sort -u)

    ALL_PRESENT=true
    while IFS= read -r required; do
      [[ -z "$required" ]] && continue
      if ! grep -Fxq "$required" <<<"$CURRENT"; then
        ALL_PRESENT=false
        break
      fi
    done <<<"$REQUIRED"

    if $ALL_PRESENT; then
      jq '.buildtovalue_plan.status = "approved"' "$PLAN_FILE" > "$TMP_FILE"
      mv "$TMP_FILE" "$PLAN_FILE"
      STATUS_MSG="✅ Plan fully approved"
    else
      COUNT_REQUIRED=$(wc -l <<<"$REQUIRED" | tr -d ' ')
      COUNT_CURRENT=$(wc -l <<<"$CURRENT" | tr -d ' ')
      STATUS_MSG="⏳ Plan partially approved (${COUNT_CURRENT}/${COUNT_REQUIRED})"
    fi
  fi
fi

echo "$STATUS_MSG"
