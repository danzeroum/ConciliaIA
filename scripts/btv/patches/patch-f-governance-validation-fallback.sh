#!/usr/bin/env bash
# ===============================================================
# 🧩 PATCH-F - Fallback de Validação de Governança (Codex Draft)
# ===============================================================
set -euo pipefail

echo ""
echo "🔧 Executando validação alternativa do governance.yaml..."
echo "=========================================================="

YAML_FILE=".buildtovalue/config/governance.yaml"
TMP_JSON="/tmp/governance.json"

if command -v yq >/dev/null 2>&1; then
  yq eval -o=json "$YAML_FILE" > "$TMP_JSON"
else
  python3 - <<'PY'
import json
import subprocess
import sys

try:
    import yaml
except ModuleNotFoundError:
    print("⚠️  Dependência PyYAML ausente. Instalando...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"❌ Falha ao instalar PyYAML: {exc}")
    import yaml

with open(".buildtovalue/config/governance.yaml") as stream:
    data = yaml.safe_load(stream)

with open("/tmp/governance.json", "w") as output:
    json.dump(data, output)
PY
fi

python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore
except ModuleNotFoundError:
    print("⚠️  Dependência jsonschema não encontrada. Instalando...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        print(f"❌ Falha ao instalar jsonschema: {exc}")
        sys.exit(1)
    import jsonschema  # type: ignore

from jsonschema import ValidationError

schema_candidates = [
    Path(".buildtovalue/schemas/governance.schema.json"),
    Path(".buildtovalue/schemas/btv-governance.schema.json"),
]

for candidate in schema_candidates:
    if candidate.exists():
        schema_path = candidate
        break
else:
    print("❌ Nenhum schema de governança encontrado.")
    sys.exit(1)

data_path = Path("/tmp/governance.json")

try:
    with schema_path.open() as schema_file, data_path.open() as data_file:
        schema = json.load(schema_file)
        data = json.load(data_file)
        jsonschema.validate(instance=data, schema=schema)
    print("✅ governance.yaml válido (fallback Python).")
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

rm -f "$TMP_JSON"

echo ""
echo "✅ PATCH-F concluído — modo Draft ativado."
