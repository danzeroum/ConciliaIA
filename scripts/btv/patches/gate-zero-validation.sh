#!/bin/bash
# GATE-ZERO: Validação final antes da codificação da GUI
set -euo pipefail

echo "🚦 GATE ZERO: Validação Pré-Codificação da GUI"
echo "==============================================="

FAILED=0

# Check 1: PostgreSQL ou .jsonl decidido?
echo -n "1️⃣ Decisão PostgreSQL vs .jsonl ... "
if [ -f "scripts/database/init-ledger-schema.sql" ]; then
    echo "✅ PostgreSQL (schema presente)"
elif [ -d ".buildtovalue/ledger/decisions" ]; then
    echo "⚠️  .jsonl (considere migrar para PostgreSQL)"
else
    echo "❌ NENHUM sistema de ledger encontrado"
    FAILED=$((FAILED + 1))
fi

# Check 2: Versões harmonizadas?
echo -n "2️⃣ Versões harmonizadas para v7.1 ... "
if grep -q "BuildToValue v7.0" README.md docs/**/*.md 2>/dev/null; then
    echo "❌ Arquivos v7.0 detectados"
    FAILED=$((FAILED + 1))
else
    echo "✅ Todos em v7.1"
fi

# Check 3: Templates base presentes?
echo -n "3️⃣ Templates base (.env.example, governance.yaml) ... "
if [ -f ".env.example" ] && [ -f ".buildtovalue/config/governance.yaml" ]; then
    echo "✅ Presentes"
else
    echo "❌ Faltando"
    FAILED=$((FAILED + 1))
fi

# Check 4: SCRIPTS-REFERENCE.md atualizado?
echo -n "4️⃣ SCRIPTS-REFERENCE.md atualizado ... "
if [ -f "SCRIPTS-REFERENCE.md" ]; then
    LAST_UPDATE=$(grep "Gerado em:" SCRIPTS-REFERENCE.md | head -1 || echo "")
    if [ -n "$LAST_UPDATE" ]; then
        echo "✅ Presente ($LAST_UPDATE)"
    else
        echo "⚠️  Presente mas sem timestamp"
    fi
else
    echo "❌ Ausente"
    FAILED=$((FAILED + 1))
fi

# Check 5: Checksums disponíveis?
echo -n "5️⃣ Script de checksums disponível ... "
if [ -f "scripts/tools/calculate-policy-checksums.sh" ]; then
    echo "✅ Presente"
else
    echo "❌ Ausente"
    FAILED=$((FAILED + 1))
fi

# Check 6: Contratos da GUI?
echo -n "6️⃣ Contratos da GUI (OpenAPI + telemetry) ... "
if [ -f "specs/operator-gui/openapi.yaml" ] && [ -f "contracts/operator-gui/telemetry.json" ]; then
    echo "✅ Presentes"
else
    echo "❌ Faltando"
    FAILED=$((FAILED + 1))
fi

# Check 7: what-matters.json presente?
echo -n "7️⃣ what-matters.json presente ... "
if [ -f ".buildtovalue/reports/what-matters.json" ]; then
    echo "✅ Presente"
else
    echo "❌ Ausente"
    FAILED=$((FAILED + 1))
fi

# Check 8: ownership-map.md presente?
echo -n "8️⃣ ownership-map.md presente ... "
if [ -f "docs/architecture/ownership-map.md" ]; then
    echo "✅ Presente"
else
    echo "❌ Ausente"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ GATE ZERO PASSOU: Pronto para codificar a GUI"
    exit 0
else
    echo "❌ GATE ZERO FALHOU: $FAILED checks falharam"
    echo ""
    echo "Ações necessárias:"
    echo "  1. Execute PATCH-A (migração PostgreSQL)"
    echo "  2. Execute PATCH-B (harmonização)"
    echo "  3. Execute PATCH-C (contratos GUI)"
    echo "  4. Re-execute este gate"
    exit 1
fi
