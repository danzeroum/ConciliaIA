#!/bin/bash
# Validar especificação

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <spec-file>" >&2
  exit 1
fi

SPEC_FILE="$1"

if [[ $SPEC_FILE == *.yaml ]] || [[ $SPEC_FILE == *.yml ]]; then
  if command -v npx >/dev/null 2>&1; then
    npx @apidevtools/swagger-cli validate "$SPEC_FILE"
  else
    echo "⚠️  swagger-cli not installed (npx missing). Skipping validation." >&2
  fi
elif [[ $SPEC_FILE == *.json ]]; then
  if command -v npx >/dev/null 2>&1; then
    npx ajv-cli validate -s "$SPEC_FILE"
  else
    echo "⚠️  ajv-cli not installed (npx missing). Skipping validation." >&2
  fi
else
  echo "❌ Unsupported specification format: $SPEC_FILE" >&2
  exit 1
fi
