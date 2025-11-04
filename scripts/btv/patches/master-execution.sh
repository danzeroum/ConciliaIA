#!/bin/bash
# MASTER SCRIPT: Execução completa de todas as correções
set -euo pipefail

echo "🚀 BuildToValue v7.1 - Preparação Final para BTV-Operator-GUI"
echo "=============================================================="
echo ""

# Passo 1: Decisão Arquitetural
echo "📍 PASSO 1: Migração do Ledger para PostgreSQL"
bash scripts/patches/patch-a-postgres-migration.sh
echo ""

# Passo 2: Harmonização
echo "📍 PASSO 2: Harmonização de Versões e Templates"
bash scripts/patches/patch-b-harmonization.sh
echo ""

# Passo 3: Contratos da GUI
echo "📍 PASSO 3: Criação de Contratos da GUI"
bash scripts/patches/patch-c-gui-contracts.sh
echo ""

# Passo 4: Validação Final
echo "📍 PASSO 4: Gate Zero - Validação Final"
bash scripts/patches/gate-zero-validation.sh
echo ""

echo "=========================================="
echo "✅ TODAS AS CORREÇÕES CONCLUÍDAS"
echo ""
echo "Próximos passos:"
echo "  1. Commit das alterações:"
echo "     git add -A"
echo "     git commit -m 'feat: preparação final para BTV-Operator-GUI'"
echo ""
echo "  2. Iniciar desenvolvimento da GUI:"
echo "     Consulte specs/operator-gui/openapi.yaml"
echo "     Consulte contracts/operator-gui/telemetry.json"
echo ""
echo "  3. A GUI pode agora consultar:"
echo "     - PostgreSQL (ledger_decisions, ledger_prompts)"
echo "     - .buildtovalue/reports/what-matters.json"
echo "     - docs/architecture/ownership-map.md"
echo ""
echo "🎉 Sistema pronto para codificação da BTV-Operator-GUI!"
