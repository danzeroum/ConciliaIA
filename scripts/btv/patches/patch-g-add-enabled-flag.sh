#!/usr/bin/env bash
# ===============================================================
# 🧩 PATCH-G - Adiciona flag 'enabled' ao specification_policy
# ===============================================================
# Corrige erro: missingProperty: 'enabled'
# BuildToValue v7.1 compliance
# ===============================================================

set -euo pipefail

echo ""
echo "🧩 Executando PATCH-G (Add 'enabled' flag ao specification_policy)"
echo "=================================================================="

FILE=".buildtovalue/config/governance.yaml"

add_enabled_flag() {
  local block="$1"
  local label="$2"
  local temp_file

  if grep -A5 "^${block}:" "$FILE" | grep -q '^[[:space:]]\+enabled:'; then
    echo "✅ ${label} já contém 'enabled'."
    return
  fi

  echo "⚙️  Inserindo 'enabled: true' em ${label}..."
  temp_file=$(mktemp)
  awk -v target="${block}" '
    $0 ~ "^" target ":" {
      print $0
      print "  enabled: true"
      next
    }
    {print}
  ' "$FILE" > "$temp_file"
  mv "$temp_file" "$FILE"
  echo "✅ Flag 'enabled: true' adicionada em ${label}."
}

if grep -q "^specification_policy:" "$FILE"; then
  add_enabled_flag "specification_policy" "specification_policy"
fi

if grep -q "^planning_policy:" "$FILE"; then
  add_enabled_flag "planning_policy" "planning_policy"
fi

echo ""
echo "🔍 Validando schema (modo Python)..."
python3 - <<'PY'
import json
import subprocess
import sys


def ensure_dependency(module: str, package: str) -> None:
    try:
        __import__(module)
    except ImportError:
        print(f"⚠️  Dependência '{module}' ausente — instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


enable_pairs = (("yaml", "PyYAML"), ("jsonschema", "jsonschema"))
for module, package in enable_pairs:
    ensure_dependency(module, package)

from jsonschema import validate, ValidationError  # type: ignore
import yaml  # type: ignore

schema_path = ".buildtovalue/schemas/governance.schema.json"
data_path = ".buildtovalue/config/governance.yaml"

try:
    with open(schema_path) as schema_file, open(data_path) as data_file:
        schema = json.load(schema_file)
        data = yaml.safe_load(data_file)
        validate(instance=data, schema=schema)
    print("✅ governance.yaml válido (v7.1 final).")
except ValidationError as err:
    print(f"❌ Erro de schema: {err.message}")
    sys.exit(1)
except FileNotFoundError as err:
    print(f"❌ Arquivo não encontrado: {err.filename}")
    sys.exit(1)
except Exception as err:
    print(f"⚠️  Falha inesperada: {err}")
    sys.exit(1)
PY

echo ""
echo "✅ PATCH-G concluído com sucesso."
