#!/bin/bash
# BuildToValue v7.1 - IA Fallback Handler
# Tenta múltiplas IAs com fallback automático

set -e

MAX_WAIT_SECONDS=300

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-wait-seconds)
      MAX_WAIT_SECONDS="$2"
      shift 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL[@]}"

PRIMARY_IA=$1
PERSONA=$2
TASK=$3
MAX_RETRIES=${4:-3}
OUTPUT_FILE=${5:-.buildtovalue/temp/ia-output.md}

if [ -z "$PRIMARY_IA" ] || [ -z "$PERSONA" ] || [ -z "$TASK" ]; then
  echo "Usage: $0 <primary-ia> <persona> <task> [max-retries] [output-file]"
  echo "Example: $0 claude ia-developer 'Implement auth' 3"
  exit 1
fi

declare -A FALLBACK_CHAIN=(
  ["claude"]="gemini"
  ["gemini"]="deepseek"
  ["deepseek"]="chatgpt"
  ["chatgpt"]="claude"
  ["maritaca"]="claude"
)

CURRENT_IA=$PRIMARY_IA
mkdir -p "$(dirname "$OUTPUT_FILE")"

for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
  echo "🔄 Attempt $attempt/$MAX_RETRIES with: $CURRENT_IA"
  echo ""

  START_TIME=$(date +%s)

  echo "📦 Generating context package..."
  ./scripts/orchestrator/generate-context-package.sh "$PERSONA" "$TASK"

  echo ""
  echo "=========================================="
  echo "📋 PROMPT READY FOR: $CURRENT_IA"
  echo "=========================================="
  echo ""
  echo "1. Open your $CURRENT_IA interface"
  echo "2. Copy the content from:"
  echo "   .buildtovalue/packages/current/COMPLETE-PROMPT.md"
  echo ""
  echo "3. Paste the IA response into:"
  echo "   $OUTPUT_FILE"
  echo ""
  echo "4. Press ENTER when ready to validate..."
  if [[ "$MAX_WAIT_SECONDS" -gt 0 ]]; then
    if ! read -r -t "$MAX_WAIT_SECONDS"; then
      echo "⏱️  Timeout de espera humana (${MAX_WAIT_SECONDS}s) atingido. Encerrando com falha."
      if [[ -x "./scripts/ledger/auto-log-decision.sh" ]]; then
        ./scripts/ledger/auto-log-decision.sh --event "assistant_flow_timeout" --meta "wait_seconds=$MAX_WAIT_SECONDS"
      fi
      exit 124
    fi
  else
    read -r
  fi

  echo ""
  echo "🔍 Validating output..."

  if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ Output file not found: $OUTPUT_FILE"
    echo "   Did you save the IA response?"
    echo ""
    echo "Try fallback IA? (y/n)"
    read -r CONTINUE

    if [ "$CONTINUE" != "y" ]; then
      exit 1
    fi

    CURRENT_IA=${FALLBACK_CHAIN[$CURRENT_IA]}
    continue
  fi

  if ./scripts/validation/validate-ia-output.sh "$OUTPUT_FILE" "$PERSONA"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo "✅ SUCCESS with $CURRENT_IA"
    echo ""

    if [ -f "scripts/analytics/track-ia-performance.sh" ]; then
      ./scripts/analytics/track-ia-performance.sh \
        "$CURRENT_IA" \
        "$PERSONA" \
        "$(echo "$TASK" | cut -c1-50)" \
        "success" \
        0.90 \
        "$DURATION"
    fi

    if [ -f ".buildtovalue/automation/context-bridge.sh" ]; then
      ./.buildtovalue/automation/context-bridge.sh "$CURRENT_IA" "codex" "$TASK"
    fi

    echo "📄 Valid output saved at: $OUTPUT_FILE"
    echo "🚀 Ready for Codex implementation"
    exit 0
  fi

  echo ""
  echo "❌ Validation failed for $CURRENT_IA"

  if [ -f "scripts/analytics/track-ia-performance.sh" ]; then
    ./scripts/analytics/track-ia-performance.sh \
      "$CURRENT_IA" \
      "$PERSONA" \
      "$(echo "$TASK" | cut -c1-50)" \
      "failed" \
      0.30 \
      "$(( $(date +%s) - START_TIME ))"
  fi

  if [ $attempt -lt $MAX_RETRIES ]; then
    NEXT_IA=${FALLBACK_CHAIN[$CURRENT_IA]}
    echo ""
    echo "Try fallback to ${NEXT_IA:-none}? (y/n)"
    read -r CONTINUE

    if [ "$CONTINUE" != "y" ]; then
      echo "Aborting..."
      exit 1
    fi

    CURRENT_IA=${NEXT_IA:-$CURRENT_IA}
  fi
done

echo ""
echo "💥 ALL IAs FAILED"
echo "   Attempted: $MAX_RETRIES times"
echo "   Last IA: $CURRENT_IA"
echo ""
echo "Suggestions:"
echo "  - Review the task complexity"
echo "  - Check if context package is clear"
echo "  - Try manual prompt refinement"
echo ""
exit 1
