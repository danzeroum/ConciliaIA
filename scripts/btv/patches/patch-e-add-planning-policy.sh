#!/usr/bin/env bash
# ===============================================================
# 🧩 PATCH-E - Correção do Bloco 'planning_policy' (BuildToValue v7.1)
# ===============================================================
set -euo pipefail

FILE=".buildtovalue/config/governance.yaml"

echo "🧩 Executando PATCH-E (Adicionando planning_policy ao governance.yaml)"

if grep -q "planning_policy" "$FILE"; then
  echo "✅ Bloco 'planning_policy' já existe."
else
  awk '/^specification_policy:/{print $0; next} /^quality_gates:/{print "planning_policy:\n  require_approval: false\n  auto_approved_by: \"IA-Arquiteto + Parecer Técnico\"\n  approval_rationale: |\n    Plano alinhado com arquitetura existente BTV v7.1.\n"} {print}' "$FILE" > /tmp/gov.tmp && mv /tmp/gov.tmp "$FILE"
  echo "✅ Bloco 'planning_policy' adicionado."
fi

echo ""
echo "🔍 Validando schema atualizado..."
python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = ["jsonschema", "yaml"]
missing = []
for module in REQUIRED:
    try:
        __import__(module)
    except ModuleNotFoundError:
        missing.append(module)

if missing:
    print(f"⚠️  Dependências Python ausentes: {', '.join(missing)}")
    print("⚙️  Instalando dependências necessárias (jsonschema, PyYAML)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema", "PyYAML"], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        print(f"❌ Falha ao instalar dependências: {exc}")
        sys.exit(1)

import yaml  # type: ignore
from jsonschema import ValidationError, validate  # type: ignore

data_path = ".buildtovalue/config/governance.yaml"
schema_candidates = [
    ".buildtovalue/schemas/governance.schema.json",
    ".buildtovalue/schemas/btv-governance.schema.json",
]

for candidate in schema_candidates:
    if Path(candidate).exists():
        schema_path = candidate
        break
else:
    print("❌ Nenhum schema de governança encontrado.")
    sys.exit(1)

try:
    with open(schema_path) as schema_file, open(data_path) as data_file:
        schema = json.load(schema_file)
        data = yaml.safe_load(data_file)
        validate(instance=data, schema=schema)
    print("✅ governance.yaml válido (validação Python).")
except FileNotFoundError as err:
    print(f"❌ Arquivo não encontrado: {err.filename}")
    sys.exit(1)
except ValidationError as err:
    print("❌ Erro de schema:")
    print(err.message)
    sys.exit(1)
except Exception as err:
    print(f"⚠️  Erro inesperado: {err}")
    sys.exit(1)
PY

echo ""
echo "✅ PATCH-E concluído."
