#!/bin/bash
# Criar novo plano declarativo

set -euo pipefail

TEMPLATE="backend-service"
EPIC="New Feature"
OWNER=$(git config user.email 2>/dev/null || echo "owner@company.com")
DOMAIN="domain"
COMPONENT="component"
API="api"

while [[ $# -gt 0 ]]; do
  case $1 in
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --template=*)
      TEMPLATE="${1#*=}"
      shift
      ;;
    --epic)
      EPIC="$2"
      shift 2
      ;;
    --epic=*)
      EPIC="${1#*=}"
      shift
      ;;
    --owner)
      OWNER="$2"
      shift 2
      ;;
    --owner=*)
      OWNER="${1#*=}"
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
    --component)
      COMPONENT="$2"
      shift 2
      ;;
    --component=*)
      COMPONENT="${1#*=}"
      shift
      ;;
    --api)
      API="$2"
      shift 2
      ;;
    --api=*)
      API="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if command -v uuidgen >/dev/null 2>&1; then
  ID_SUFFIX=$(uuidgen | cut -d'-' -f1)
else
  ID_SUFFIX=$(python - <<'PY'
import secrets
print(secrets.token_hex(3))
PY
)
fi

PLAN_ID="PLAN-$(date +%Y-%m-%d)-${ID_SUFFIX}"
PLAN_FILE=".buildtovalue/plans/active/${PLAN_ID}.json"
TEMPLATE_FILE=".buildtovalue/plans/templates/${TEMPLATE}.json"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "❌ Template not found: $TEMPLATE_FILE" >&2
  exit 1
fi

mkdir -p "$(dirname "$PLAN_FILE")"
cp "$TEMPLATE_FILE" "$PLAN_FILE"

CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

python - <<PY
from pathlib import Path
import re

plan_path = Path(${PLAN_FILE@Q})
content = plan_path.read_text()

def title_case(value: str) -> str:
    parts = re.split(r'[_\-\s]+', value)
    return ''.join(part.capitalize() for part in parts if part)

def camel_case(value: str) -> str:
    titled = title_case(value)
    return titled

replacements = {
    'PLAN_ID': ${PLAN_ID@Q},
    'EPIC': ${EPIC@Q},
    'OWNER': ${OWNER@Q},
    'CREATED_AT': ${CREATED_AT@Q},
    'DOMAIN': ${DOMAIN@Q},
    'domain': ${DOMAIN@Q},
    'Domain': camel_case(${DOMAIN@Q}),
    'ID': ${PLAN_ID@Q},
    'Service': camel_case(${DOMAIN@Q}) + 'Service',
    'Controller': camel_case(${DOMAIN@Q}) + 'Controller',
    'Repository': camel_case(${DOMAIN@Q}) + 'Repository',
    'COMPONENT': ${COMPONENT@Q},
    'component': ${COMPONENT@Q},
    'Component': camel_case(${COMPONENT@Q}),
    'API': ${API@Q},
}

for key, value in replacements.items():
    content = content.replace(f'{{{{{key}}}}}', value)

plan_path.write_text(content)
PY

cat <<MSG
✅ Plan created: $PLAN_FILE
Edit plan, then validate: ./scripts/planning/validate-plan.sh $PLAN_ID
MSG
