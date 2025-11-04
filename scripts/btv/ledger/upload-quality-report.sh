#!/bin/bash
# BuildToValue Quality Report uploader (JSONL + jq)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <report-type> <report-file>" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required to upload quality reports" >&2
  exit 1
fi

REPORT_TYPE="$1"
REPORT_FILE="$2"

if [ ! -f "$REPORT_FILE" ]; then
  echo "❌ Report file not found: $REPORT_FILE" >&2
  exit 1
fi

TIMESTAMP=$(date -Iseconds)
LEDGER_DIR=".buildtovalue/ledger/reports"
mkdir -p "$LEDGER_DIR"
LEDGER_FILE="$LEDGER_DIR/$(date +%Y-%m).jsonl"

VERSION="$(cat .buildtovalue/VERSION 2>/dev/null || echo "7.2.0")"
SOURCE="${LEDGER_SOURCE:-pipeline}"
FILENAME="$(basename "$REPORT_FILE")"
SIZE_BYTES=$(stat -c%s "$REPORT_FILE")
HASH_VALUE=$(sha256sum "$REPORT_FILE" | awk '{print $1}')

PAYLOAD=$(jq -n \
  --arg ts "$TIMESTAMP" \
  --arg type "$REPORT_TYPE" \
  --arg file "$REPORT_FILE" \
  --arg name "$FILENAME" \
  --arg version "$VERSION" \
  --arg source "$SOURCE" \
  --arg hash "$HASH_VALUE" \
  --argjson size "$SIZE_BYTES" \
  '{
    timestamp: $ts,
    type: $type,
    file: $file,
    filename: $name,
    size_bytes: $size,
    digest: {sha256: $hash},
    status: "uploaded",
    version: $version,
    source: $source
  }')

echo "$PAYLOAD" >> "$LEDGER_FILE"

TOTAL=$(jq -s 'length' "$LEDGER_FILE")
TYPE_COUNT=$(jq -s --arg type "$REPORT_TYPE" 'map(select(.type == $type)) | length' "$LEDGER_FILE")

echo "📊 Quality report logged: $REPORT_TYPE → $REPORT_FILE"
echo "🗂  Ledger: $LEDGER_FILE (total entries: $TOTAL, $REPORT_TYPE entries: $TYPE_COUNT)"
