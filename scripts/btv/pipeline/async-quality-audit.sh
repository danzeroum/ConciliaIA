#!/usr/bin/env bash
set -euo pipefail

# Resolve repository root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$REPO_ROOT"

if ! source "scripts/utils/common.sh" 2>/dev/null; then
  echo "❌ scripts/utils/common.sh não encontrado" >&2
  exit 1
fi

log_info "🕵️  Executando Auditor Profundo (Async)..."
log_info "Projeto: ${PROJECT_TYPE:-internal-tool}"

# Garantir que os stubs atuais sejam executáveis
chmod +x scripts/auditor/run-mutation-tests.sh
chmod +x scripts/auditor/run-bdd-validation.sh
chmod +x scripts/auditor/quarantine-flaky.sh

# TODO: Ler btv-config.yaml para ativar/desativar gates dinamicamente

log_info "🧬 Executando Testes de Mutação (Stub)..."
./scripts/auditor/run-mutation-tests.sh || {
  log_error "Falha nos Testes de Mutação"
}

log_info "📖 Executando Validação BDD (Stub)..."
./scripts/auditor/run-bdd-validation.sh || {
  log_error "Falha na Validação BDD"
}

log_info "📉 Verificando Testes Flaky (Stub)..."
./scripts/auditor/quarantine-flaky.sh || {
  log_error "Falha na verificação de Flaky Tests"
}

# (Outros gates async como performance, ethics_full_audit virão depois)

log_success "✅ Auditoria Profunda (Async) concluída."
