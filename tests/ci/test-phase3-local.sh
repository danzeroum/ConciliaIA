#!/bin/bash
set -euo pipefail
echo "🔷 Executando testes locais (pytest)..."
PYTHON=$(command -v python3 || command -v python)
"$PYTHON" -m pip install -U pip pytest >/dev/null
"$PYTHON" -m pytest -v tests/compliance
