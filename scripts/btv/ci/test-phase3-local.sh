#!/usr/bin/env bash
# ==============================================================================
# BuildToValue v7.4.1-Platinum-Safe
# Local Compliance & Certification Tester – Fase 3 (GDPR, SOX, ISO27001)
# Compatível com act + Windows/Linux + venv fallback
# ==============================================================================

set -euo pipefail
IFS=$'\n\t'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKFLOW_FILE="$ROOT_DIR/.github/workflows/phase3-compliance.yml"
BTV_DIR="$ROOT_DIR/.buildtovalue"
VENV_DIR="$ROOT_DIR/.venv"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
section() { echo -e "\n\033[1;36m🔷 $1\033[0m"; }
success() { echo -e "\033[1;32m✅ $1\033[0m"; }
warn()    { echo -e "\033[1;33m⚠️  $1\033[0m"; }
error()   { echo -e "\033[1;31m❌ $1\033[0m"; }
require() { command -v "$1" >/dev/null 2>&1 || { error "Dependência ausente: $1"; exit 1; }; }

# ------------------------------------------------------------------------------
# 1️⃣ Verificar ambiente
# ------------------------------------------------------------------------------
section "Verificando ambiente local..."

for dep in jq tar gzip; do require "$dep"; done

if ! command -v act >/dev/null 2>&1; then
  warn "'act' não encontrado — execução seguirá via pytest/venv"
  ACT_AVAILABLE=false
else
  ACT_AVAILABLE=true
fi

# ------------------------------------------------------------------------------
# 2️⃣ Preparar estrutura mínima
# ------------------------------------------------------------------------------
section "Preparando estrutura .buildtovalue..."
mkdir -p \
  "$BTV_DIR/archives" \
  "$BTV_DIR/compliance"/{reports,evidence,certification-packages} \
  "$ROOT_DIR/scripts/compliance/frameworks"
touch "$BTV_DIR/ledger.jsonl"
success "Estrutura pronta."

# ------------------------------------------------------------------------------
# 3️⃣ Preparar Python local / venv
# ------------------------------------------------------------------------------
section "Verificando ambiente Python..."
PYTEST_CMD="pytest"

if ! command -v pytest >/dev/null 2>&1; then
  warn "pytest não encontrado globalmente — criando ambiente virtual .venv"
  python3 -m venv "$VENV_DIR"
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate"
  pip install --upgrade pip setuptools wheel
  pip install --break-system-packages pytest jq || pip install pytest jq
  PYTEST_CMD="$VENV_DIR/bin/pytest"
else
  pip install --break-system-packages -q pytest jq || true
fi

PY_VER="$(python3 -V 2>/dev/null || echo "Python N/D")"
success "Python OK ($PY_VER)"
success "pytest OK ($($PYTEST_CMD --version 2>/dev/null || echo "verificado"))"

# ------------------------------------------------------------------------------
# 4️⃣ Executar workflow com act (se disponível)
# ------------------------------------------------------------------------------
if [ "$ACT_AVAILABLE" = true ]; then
  section "Executando workflow completo com act..."
  pushd "$ROOT_DIR" >/dev/null
  act push -W "$WORKFLOW_FILE" --pull=false || {
    warn "Falha no act – alternando para pytest local."
    ACT_AVAILABLE=false
  }
  popd >/dev/null
fi

# ------------------------------------------------------------------------------
# 5️⃣ Fallback: pytest local
# ------------------------------------------------------------------------------
if [ "$ACT_AVAILABLE" = false ]; then
  section "Executando testes locais (pytest)..."
  pushd "$ROOT_DIR" >/dev/null
  "$PYTEST_CMD" -v tests/compliance || {
    error "Falha nos testes de compliance."
    exit 1
  }
  popd >/dev/null
  success "Todos os testes pytest passaram."
fi

# ------------------------------------------------------------------------------
# 6️⃣ Gerar relatório e pacotes
# ------------------------------------------------------------------------------
section "Gerando relatório unificado..."
bash "$ROOT_DIR/scripts/compliance/unified-compliance-scanner.sh" report || warn "Falha ao gerar relatório."

section "Listando pacotes de certificação..."
bash "$ROOT_DIR/scripts/compliance/certification-packager.sh" list || warn "Falha ao listar pacotes."

# ------------------------------------------------------------------------------
# 7️⃣ Sumário final
# ------------------------------------------------------------------------------
section "Sumário Final"
if ls "$BTV_DIR/compliance/reports/unified-compliance-"*.json >/dev/null 2>&1; then
  REPORT=$(ls -t "$BTV_DIR"/compliance/reports/unified-compliance-*.json | head -1)
  STATUS=$(jq -r '.summary.overall_status' "$REPORT" 2>/dev/null || echo "unknown")
  SCORE=$(jq -r '.summary.average_score' "$REPORT" 2>/dev/null || echo "N/A")
  echo "📊 Relatório: $REPORT"
  echo "🔖 Status: $STATUS"
  echo "💯 Score médio: $SCORE%"
else
  warn "Relatório unificado não encontrado."
fi

if ls "$BTV_DIR/compliance/certification-packages/"*.tar.gz >/dev/null 2>&1; then
  success "Pacotes de certificação gerados com sucesso."
else
  warn "Nenhum pacote de certificação encontrado."
fi

echo ""
success "Teste local da Fase 3 concluído!"
echo "🧾 Relatórios em: $BTV_DIR/compliance/reports/"
