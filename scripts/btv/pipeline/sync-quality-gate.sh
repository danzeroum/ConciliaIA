#!/bin/bash
# Porteiro Rápido - Pipeline Síncrono (<90s)
# Valida integridade mínima antes do merge

set -euo pipefail

PROJECT_TYPE="internal-tool"
STRICT_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --project-type)
      PROJECT_TYPE="$2"
      shift 2
      ;;
    --strict)
      STRICT_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$STRICT_MODE" == true ]]; then
  echo "⚙️  Strict mode habilitado"
fi

echo "🚀 Executando Porteiro Rápido para: $PROJECT_TYPE"
START_TIME=$SECONDS

# 1. Validação de Segurança Básica
echo "🔒 Validando segurança básica..."
./scripts/security/basic-scan.sh --fail-on-critical

# 2. Testes Unitários Rápidos
echo "🧪 Executando testes unitários críticos..."
./scripts/testing/run-critical-tests.sh --timeout 30

# 3. Análise Estática
echo "📊 Executando análise estática..."
./scripts/quality/static-analysis.sh --quick

# 4. Validação de Cobertura Mínima
echo "📈 Validando cobertura mínima..."
python src/quality/intelligence/AdaptiveQualityGates.py --validate-minimum --project-type "$PROJECT_TYPE"

# 5. Hardening Básico
echo "🛠️ Aplicando hardening básico..."
./scripts/development/harden-immediately.sh --critical-only

ELAPSED_TIME=$((SECONDS - START_TIME))
echo "✅ Porteiro Rápido concluído em ${ELAPSED_TIME}s"

# Gerar relatório
mkdir -p reports
cat > reports/sync-quality-report.json << EOF_JSON
{
  "timestamp": "$(date -Iseconds)",
  "project_type": "$PROJECT_TYPE",
  "strict_mode": $STRICT_MODE,
  "duration_seconds": $ELAPSED_TIME,
  "status": "passed",
  "checks": {
    "security_scan": "passed",
    "unit_tests": "passed", 
    "static_analysis": "passed",
    "coverage_validation": "passed",
    "hardening": "passed"
  }
}
EOF_JSON
