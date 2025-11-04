#!/bin/bash
# BuildToValue v7.1 - Smart Context Generator (IA-Agnostic)

set -e

PERSONA=$1
TASK=$2
FORMAT=${3:-"markdown"}

if [ -z "$PERSONA" ] || [ -z "$TASK" ]; then
  echo "Usage: $0 <persona> <task> [format]"
  echo "Formats: markdown, json, plain"
  exit 1
fi

./scripts/orchestrator/generate-context-package.sh "$PERSONA" "$TASK"

case $FORMAT in
  markdown)
    cat .buildtovalue/packages/current/COMPLETE-PROMPT.md
    ;;
  json)
    jq -n \
      --arg persona "$PERSONA" \
      --arg task "$TASK" \
      --rawfile content .buildtovalue/packages/current/COMPLETE-PROMPT.md \
      '{persona: $persona, task: $task, content: $content}'
    ;;
  plain)
    sed 's/^#\+//; s/```.*$//; /^$/d' .buildtovalue/packages/current/COMPLETE-PROMPT.md
    ;;
  *)
    echo "❌ Unknown format: $FORMAT"
    exit 1
    ;;
esac
