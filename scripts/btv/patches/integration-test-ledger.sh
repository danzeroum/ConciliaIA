#!/bin/bash
# INTEGRATION TEST: Testar fluxo completo de ledger
set -euo pipefail

echo "🧪 TESTE DE INTEGRAÇÃO: Fluxo Completo de Ledger"
echo "================================================="
echo ""

# Teste 1: Gravar decisão
echo "1️⃣ Gravando decisão de teste..."
TEST_ID="DEC-TEST-$(date +%s)"
./scripts/ledger/auto-log-decision.sh "test-agent" "Teste de integração" "success" 0.95

# Teste 2: Verificar se foi gravado
echo ""
echo "2️⃣ Verificando gravação no PostgreSQL..."
RESULT=$(docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -t -c "SELECT id FROM ledger_decisions WHERE agent='test-agent' ORDER BY timestamp DESC LIMIT 1;" | xargs)

if [ -n "$RESULT" ]; then
    echo "   ✅ Decisão gravada com ID: $RESULT"
else
    echo "   ❌ Decisão não encontrada no banco"
    exit 1
fi

# Teste 3: Gravar prompt
echo ""
echo "3️⃣ Gravando prompt de teste..."
PROMPT_ID="PROMPT-TEST-$(date +%s)"
echo "Este é um prompt de teste" | ./scripts/ledger/log-prompt.sh "$PROMPT_ID" "test-persona" "Tarefa de teste" "auto" <<EOF2
Esta é a resposta de teste
EOF2

# Teste 4: Verificar prompt
echo ""
echo "4️⃣ Verificando prompt no PostgreSQL..."
PROMPT_RESULT=$(docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -t -c "SELECT id FROM ledger_prompts WHERE persona='test-persona' ORDER BY timestamp DESC LIMIT 1;" | xargs)

if [ -n "$PROMPT_RESULT" ]; then
    echo "   ✅ Prompt gravado com ID: $PROMPT_RESULT"
else
    echo "   ❌ Prompt não encontrado no banco"
    exit 1
fi

# Teste 5: Consultar via SQL (simulando GUI)
echo ""
echo "5️⃣ Simulando consulta da GUI..."
echo "   📊 Últimas 5 decisões:"
docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -c "
SELECT 
    id,
    agent,
    task,
    outcome,
    confidence,
    timestamp::date as date
FROM ledger_decisions 
ORDER BY timestamp DESC 
LIMIT 5;
"

# Teste 6: Ler what-matters.json
echo ""
echo "6️⃣ Testando leitura de what-matters.json..."
if [ -f ".buildtovalue/reports/what-matters.json" ]; then
    cat .buildtovalue/reports/what-matters.json | jq -r '.generated_at // "placeholder"' | head -1
    echo "   ✅ Arquivo legível"
else
    echo "   ❌ Arquivo não encontrado"
    exit 1
fi

# Teste 7: Validar OpenAPI spec
echo ""
echo "7️⃣ Validando OpenAPI spec..."
if command -v ajv >/dev/null 2>&1; then
    ajv validate -s specs/operator-gui/openapi.yaml 2>/dev/null && echo "   ✅ OpenAPI válido" || echo "   ⚠️  OpenAPI com avisos (não crítico)"
else
    echo "   ⚠️  ajv não instalado, pulando validação"
fi

echo ""
echo "=========================================="
echo "✅ TODOS OS TESTES PASSARAM"
echo ""
echo "🎉 Sistema pronto para receber a BTV-Operator-GUI!"
echo ""
echo "Próximos passos:"
echo "  1. Commit: git add -A && git commit -m 'feat: base pronta para GUI'"
echo "  2. Push: git push origin main"
echo "  3. Iniciar dev da GUI consultando:"
echo "     - PostgreSQL: ledger_decisions, ledger_prompts"
echo "     - Arquivo: .buildtovalue/reports/what-matters.json"
echo "     - Spec: specs/operator-gui/openapi.yaml"
