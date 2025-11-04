#!/bin/bash
# PATCH-B: Harmonização de Versões, Templates e Inventários
set -euo pipefail

echo "🔧 PATCH-B: Harmonização e Templates"
echo "===================================="

# PATCH-B1: Padronizar versão v7.1 em todos os documentos
echo "1️⃣ Padronizando versão para v7.1..."
find docs/ README.md -type f -name "*.md" -exec sed -i.bak 's/BuildToValue v7\.0/BuildToValue v7.1/g' {} \;
find docs/ README.md -type f -name "*.bak" -delete
echo "   ✅ Versões harmonizadas"

# PATCH-B2: Criar templates base
echo "2️⃣ Criando templates base..."
mkdir -p .buildtovalue/config

# .env.example
cat > .env.example <<'ENV'
# BuildToValue v7.1 - Environment Variables
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
ENVIRONMENT=development
FREE_MODE_ENABLED=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=buildtovalue
POSTGRES_USER=btv_user
POSTGRES_PASSWORD=changeme123
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
PROMETHEUS_URL=
SLACK_WEBHOOK_URL=
ENV

# governance.yaml mínimo
cat > .buildtovalue/config/governance.yaml <<'GOV'
btv_version: "7.1"
project:
  name: buildtovalue
  description: "IA-driven development with squad orchestration"

spec_first: true
plan_first: true
harden_on_generate: true

quality_gates:
  pre_commit:
    enabled: true
    min_coverage: 0.80
  ci_cd:
    enabled: true
    required_checks:
      - unit_tests
      - integration_tests
      - security_scan

ledger_policy:
  auto_log: true
  compression: gzip
  retention_days: 365

shell_allowlist:
  - mkdir
  - cat
  - echo
  - git
  - docker
  - python3
  - node
  - npm
  - yarn
  - curl
  - grep
  - sed
  - awk
  - jq
GOV

echo "   ✅ Templates criados: .env.example, governance.yaml"

# PATCH-B3: Gerador de referência de scripts
echo "3️⃣ Criando gerador de referência de scripts..."
mkdir -p scripts/tools

cat > scripts/tools/generate-scripts-reference.sh <<'GENSH'
#!/usr/bin/env bash
set -euo pipefail

OUT="SCRIPTS-REFERENCE.md"
echo "# 🔧 Scripts Reference (autogerado)" > "$OUT"
echo "" >> "$OUT"
echo "Gerado em: $(date -Iseconds)" >> "$OUT"
echo "" >> "$OUT"
echo '```' >> "$OUT"
find scripts -type f \( -name "*.sh" -o -name "*.py" \) -print | sort >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"
echo "---" >> "$OUT"
echo "" >> "$OUT"
echo "## Scripts por Categoria" >> "$OUT"
echo "" >> "$OUT"

for dir in scripts/*/; do
    category=$(basename "$dir")
    echo "### $category" >> "$OUT"
    find "$dir" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) -print | sort | while read -r script; do
        script_name=$(basename "$script")
        # Tentar extrair descrição do cabeçalho
        desc=$(head -20 "$script" | grep -E "^#.*Função:|^#.*Purpose:" | head -1 | sed 's/^#[[:space:]]*//' || echo "")
        if [ -n "$desc" ]; then
            echo "- **$script_name**: $desc" >> "$OUT"
        else
            echo "- **$script_name**" >> "$OUT"
        fi
    done
    echo "" >> "$OUT"
done

echo "✅ Referência gerada: $OUT"
GENSH

chmod +x scripts/tools/generate-scripts-reference.sh
./scripts/tools/generate-scripts-reference.sh
git add SCRIPTS-REFERENCE.md
echo "   ✅ SCRIPTS-REFERENCE.md gerado e commitado"

# PATCH-B4: Script para calcular checksums de políticas
echo "4️⃣ Criando helper de checksums..."
cat > scripts/tools/calculate-policy-checksums.sh <<'CHECKSH'
#!/usr/bin/env bash
set -euo pipefail

echo "📋 Checksums de Políticas BuildToValue v7.1"
echo "============================================"
echo ""

if [ -f .buildtovalue/config/governance.yaml ]; then
    GOV_SHA=$(sha1sum .buildtovalue/config/governance.yaml | cut -d' ' -f1)
    echo "governance_yaml: $GOV_SHA"
else
    echo "governance_yaml: (arquivo não encontrado)"
fi

if [ -f .buildtovalue/config/invariants.yaml ]; then
    INV_SHA=$(sha1sum .buildtovalue/config/invariants.yaml | cut -d' ' -f1)
    echo "invariants_yaml: $INV_SHA"
else
    echo "invariants_yaml: (arquivo não encontrado)"
fi

echo ""
echo "💡 Use estes valores no cabeçalho de simulação:"
echo "   policy_checksums:"
echo "     governance_yaml: $GOV_SHA"
echo "     invariants_yaml: $INV_SHA"
CHECKSH

chmod +x scripts/tools/calculate-policy-checksums.sh
echo "   ✅ Helper de checksums criado"

echo ""
echo "✅ PATCH-B concluído"
