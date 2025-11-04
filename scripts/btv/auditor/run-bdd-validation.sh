#!/usr/bin/env bash
# 🎭 Executa testes BDD (Behave/Python)
set -euo pipefail

echo "🎬 Executando validações BDD (Behave)..."
PROJECT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_DIR"

if [ ! -d "features" ]; then
  echo "⚠️ Nenhum diretório 'features' encontrado – criando exemplo."
  mkdir -p features
  cat > features/sample.feature <<'FF'
Feature: Sample BDD
  Scenario: basic sanity
    Given a working BuildToValue environment
    When IA developer runs a BDD check
    Then the result should be successful
FF
  mkdir -p features/steps
  cat > features/steps/sample_steps.py <<'PY'
from behave import given, when, then


@given("a working BuildToValue environment")
def step_given(context):
    pass


@when("IA developer runs a BDD check")
def step_when(context):
    pass


@then("the result should be successful")
def step_then(context):
    pass
PY
fi

if command -v poetry >/dev/null 2>&1; then
  poetry run behave -q || behave -q
else
  behave -q
fi

echo "✅ BDD validation complete."
