#!/bin/bash
# Criar novo contrato OpenAPI/JSON Schema

set -euo pipefail

TYPE="openapi"
DOMAIN="default"
OUTPUT=""
TEMPLATE="rest-api"

while [[ $# -gt 0 ]]; do
  case $1 in
    --type)
      TYPE="$2"
      shift 2
      ;;
    --type=*)
      TYPE="${1#*=}"
      shift
      ;;
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --domain=*)
      DOMAIN="${1#*=}"
      shift
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --output=*)
      OUTPUT="${1#*=}"
      shift
      ;;
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --template=*)
      TEMPLATE="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$OUTPUT" ]]; then
  case "$TYPE" in
    openapi)
      OUTPUT=".buildtovalue/specifications/api/${DOMAIN}.openapi.yaml"
      ;;
    jsonschema)
      OUTPUT=".buildtovalue/specifications/schemas/${DOMAIN}.schema.json"
      ;;
    asyncapi)
      OUTPUT=".buildtovalue/specifications/events/${DOMAIN}.asyncapi.yaml"
      ;;
    proto)
      OUTPUT=".buildtovalue/specifications/proto/${DOMAIN}.proto"
      ;;
    interfaces)
      OUTPUT=".buildtovalue/specifications/interfaces/${DOMAIN}.types.ts"
      ;;
    *)
      echo "❌ Unsupported type: $TYPE" >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$(dirname "$OUTPUT")"

case "$TYPE" in
  openapi)
    TEMPLATE_FILE="templates/specifications/openapi-${TEMPLATE}.yaml"
    ;;
  jsonschema)
    TEMPLATE_FILE="templates/specifications/jsonschema-template.json"
    ;;
  *)
    echo "❌ Template not available for type: $TYPE" >&2
    exit 1
    ;;
 esac

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "❌ Template not found: $TEMPLATE_FILE" >&2
  exit 1
fi

cp "$TEMPLATE_FILE" "$OUTPUT"

sed -i "s/{{SERVICE_NAME}}/${DOMAIN^}/g" "$OUTPUT" 2>/dev/null || true
sed -i "s/{{DOMAIN}}/${DOMAIN}/g" "$OUTPUT" 2>/dev/null || true
sed -i "s/{{domain}}/${DOMAIN}/g" "$OUTPUT" 2>/dev/null || true
sed -i "s/{{Resource}}/${DOMAIN^}/g" "$OUTPUT" 2>/dev/null || true
sed -i "s/{{resource}}/${DOMAIN}/g" "$OUTPUT" 2>/dev/null || true

cat <<MSG
✅ Contract created: $OUTPUT
Edit and validate with: ./scripts/specification/validate-contract.sh $OUTPUT
MSG
