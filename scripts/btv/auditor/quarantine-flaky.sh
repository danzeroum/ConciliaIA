#!/usr/bin/env bash
# 🧪 Detecta e reexecuta testes flaky automaticamente (usar pytest-rerunfailures)
set -euo pipefail

echo "🔁 Detectando e reexecutando testes flaky..."
PROJECT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_DIR"

mkdir -p .buildtovalue/reports
pytest --maxfail=1 --reruns 3 --reruns-delay 2 -q \
  > .buildtovalue/reports/flaky-run.log || true

if grep -q "RERUN" .buildtovalue/reports/flaky-run.log 2>/dev/null; then
  echo "⚠️ Testes reexecutados (potencial flaky) – movendo para quarantine/"
  mkdir -p tests/quarantine
  grep "RERUN" .buildtovalue/reports/flaky-run.log | awk '{print $2}' \
    > .buildtovalue/reports/flaky-list.txt
  while read -r test_path; do
    if [ -n "$test_path" ]; then
      mv "$test_path" tests/quarantine/ 2>/dev/null || true
    fi
  done < .buildtovalue/reports/flaky-list.txt
else
  echo "✅ Nenhum teste flaky detectado."
fi
