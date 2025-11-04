#!/usr/bin/env bash
# ===============================================================
# 🧩 PATCH-D - Correções CI/CD e Governança (BuildToValue v7.1)
# ===============================================================
set -euo pipefail

echo ""
echo "🚀 Executando PATCH-D (Governança + CI/CD Resilience)"
echo "====================================================="

echo "🧩 Corrigindo governance.yaml..."

if ! grep -q "specification_policy" .buildtovalue/config/governance.yaml; then
  awk '/^quality_gates:/{print "specification_policy:\n  contract_first: \"Todo código nasce de contrato ou ADR\"\n  validation_chain: [\"Simular\", \"Validar\", \"Codex\", \"Ledger\"]\n  authority_order:\n    - \"scripts oficiais (.sh)\"\n    - \"CI/CD (quality gates)\"\n    - \"IA assistente (simulação)\"\n  security:\n    - \"Sem execução real de shell\"\n    - \"Sem acesso a FS remoto\"\n    - \"Sem manipulação de secrets\"\n  ethics:\n    - \"Privacidade > conveniência\"\n    - \"Sem viés, sem dano, explicável\""}1' .buildtovalue/config/governance.yaml > /tmp/gov.tmp && mv /tmp/gov.tmp .buildtovalue/config/governance.yaml
  echo "✅ Bloco specification_policy inserido."
else
  echo "✅ Bloco specification_policy já existe — pulando."
fi

echo ""
echo "🐘 Garantindo container PostgreSQL para CI/CD..."

if ! docker ps --format '{{.Names}}' | grep -q '^buildtovalue-postgres$'; then
  docker run -d --name buildtovalue-postgres \
    -e POSTGRES_USER=btv_user -e POSTGRES_PASSWORD=changeme123 -e POSTGRES_DB=buildtovalue \
    -p 5432:5432 postgres:16
  sleep 10
  echo "✅ Container PostgreSQL iniciado."
else
  echo "✅ Container PostgreSQL já em execução."
fi

echo ""
echo "🧠 Aplicando fallback de container nos scripts..."
for script in scripts/ledger/auto-log-decision.sh scripts/metrics/compute-what-matters.sh; do
  if [ -f "$script" ] && ! grep -q "docker ps --format" "$script"; then
    tmp=$(mktemp)
    echo '# --- BuildToValue v7.1 Resilience Fallback ---' > "$tmp"
    echo 'if ! docker ps --format "{{.Names}}" | grep -q "^buildtovalue-postgres$"; then' >> "$tmp"
    echo '  echo "⚠️  Container buildtovalue-postgres não encontrado — iniciando localmente..."' >> "$tmp"
    echo '  docker run -d --name buildtovalue-postgres -e POSTGRES_USER=btv_user -e POSTGRES_PASSWORD=changeme123 -e POSTGRES_DB=buildtovalue -p 5432:5432 postgres:16' >> "$tmp"
    echo '  sleep 10' >> "$tmp"
    echo 'fi' >> "$tmp"
    echo '' >> "$tmp"
    cat "$script" >> "$tmp"
    mv "$tmp" "$script"
    chmod +x "$script"
    echo "✅ Fallback aplicado em $script"
  else
    echo "✅ Script $script já possui fallback."
  fi

done

echo ""
echo "✅ PATCH-D concluído."
