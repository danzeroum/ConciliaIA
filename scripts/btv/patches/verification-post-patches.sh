#!/bin/bash
# VERIFICATION SCRIPT: Verificar estado após patches
set -euo pipefail

echo "🔍 VERIFICAÇÃO PÓS-PATCHES"
echo "=========================="
echo ""

# 1. Verificar PostgreSQL
echo "1️⃣ PostgreSQL Ledger Schema"
docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dt ledger_*" 2>/dev/null && echo "   ✅ Tabelas criadas" || echo "   ❌ Tabelas ausentes"

# 2. Contar decisões migradas
echo ""
echo "2️⃣ Dados Migrados"
DECISION_COUNT=$(docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -t -c "SELECT COUNT(*) FROM ledger_decisions;" 2>/dev/null | xargs || echo "0")
echo "   📊 Decisões no PostgreSQL: $DECISION_COUNT"

# 3. Verificar scripts atualizados
echo ""
echo "3️⃣ Scripts Atualizados"
if grep -q "psql" scripts/ledger/auto-log-decision.sh 2>/dev/null; then
    echo "   ✅ auto-log-decision.sh usa PostgreSQL"
else
    echo "   ❌ auto-log-decision.sh ainda usa .jsonl"
fi

if grep -q "psql" scripts/ledger/log-prompt.sh 2>/dev/null; then
    echo "   ✅ log-prompt.sh usa PostgreSQL"
else
    echo "   ❌ log-prompt.sh ainda usa .jsonl"
fi

# 4. Verificar templates
echo ""
echo "4️⃣ Templates Base"
[ -f ".env.example" ] && echo "   ✅ .env.example" || echo "   ❌ .env.example ausente"
[ -f ".buildtovalue/config/governance.yaml" ] && echo "   ✅ governance.yaml" || echo "   ❌ governance.yaml ausente"

# 5. Verificar contratos da GUI
echo ""
echo "5️⃣ Contratos da GUI"
[ -f "specs/operator-gui/openapi.yaml" ] && echo "   ✅ OpenAPI spec" || echo "   ❌ OpenAPI ausente"
[ -f "contracts/operator-gui/telemetry.json" ] && echo "   ✅ Telemetry contract" || echo "   ❌ Telemetry ausente"
[ -f ".buildtovalue/reports/what-matters.json" ] && echo "   ✅ what-matters.json" || echo "   ❌ what-matters.json ausente"
[ -f "docs/architecture/ownership-map.md" ] && echo "   ✅ ownership-map.md" || echo "   ❌ ownership-map.md ausente"

# 6. Verificar SCRIPTS-REFERENCE
echo ""
echo "6️⃣ Documentação"
if [ -f "SCRIPTS-REFERENCE.md" ]; then
    SCRIPT_COUNT=$(grep -c "\\.sh" SCRIPTS-REFERENCE.md || echo "0")
    echo "   ✅ SCRIPTS-REFERENCE.md ($SCRIPT_COUNT scripts catalogados)"
else
    echo "   ❌ SCRIPTS-REFERENCE.md ausente"
fi

# 7. Testar auto-log-decision.sh
echo ""
echo "7️⃣ Teste de Log (gravando decisão de teste)"
./scripts/ledger/auto-log-decision.sh "verification-bot" "Teste pós-patches" "success" 0.99 2>/dev/null && echo "   ✅ Log funcional" || echo "   ❌ Log falhou"

# 8. Verificar checksums disponíveis
echo ""
echo "8️⃣ Checksums de Políticas"
if [ -f "scripts/tools/calculate-policy-checksums.sh" ]; then
    ./scripts/tools/calculate-policy-checksums.sh | head -4
else
    echo "   ❌ Script de checksums ausente"
fi

echo ""
echo "=========================================="
echo "✅ Verificação concluída"
echo ""
echo "💡 Se todos os checks estão ✅, você pode começar a GUI"
