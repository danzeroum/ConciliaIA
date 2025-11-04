#!/bin/bash
# BuildToValue v7.1 - IA Performance Tracker (Simplificado)

set -e

IA_NAME=$1
PERSONA=$2
TASK=$3
OUTCOME=$4
CONFIDENCE=${5:-0.50}
DURATION=${6:-0}

if [ -z "$IA_NAME" ] || [ -z "$OUTCOME" ]; then
  echo "Usage: $0 <ia-name> <persona> <task> <outcome> [confidence] [duration]"
  exit 1
fi

ANALYTICS_FILE=".buildtovalue/analytics/ia-performance.jsonl"
mkdir -p "$(dirname "$ANALYTICS_FILE")"

cat >> "$ANALYTICS_FILE" << __JSON_EOF__
{"timestamp":"$(date -Iseconds)","ia":"$IA_NAME","persona":"$PERSONA","task":"$TASK","outcome":"$OUTCOME","confidence":$CONFIDENCE,"duration_sec":$DURATION}
__JSON_EOF__

echo "📊 Performance tracked: $IA_NAME - $OUTCOME"
