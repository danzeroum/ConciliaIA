# Inserir após instalar yq/jq (ex.: no job que usa yq):
- name: Validate yq compatibility
  run: |
    set -euo pipefail
    yq eval '.project.name' .buildtovalue/config/governance.yaml >/dev/null
    yq --version | tee -a "$GITHUB_STEP_SUMMARY"

# Inserir no job What Matters (antes de "Compute What Matters"):
- name: Validate required secrets
  run: |
    set -euo pipefail
    missing=()
    [[ -z "${PROMETHEUS_URL:-}" ]] && missing+=("PROMETHEUS_URL")
    [[ -z "${SLACK_WEBHOOK_URL:-}" ]] && missing+=("SLACK_WEBHOOK_URL")
    if [[ ${#missing[@]} -gt 0 ]]; then
      echo "::error::Missing required secrets: ${missing[*]}"
      echo "Configure em: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/settings/secrets/actions"
      exit 1
    fi
    if [[ ! "${SLACK_WEBHOOK_URL}" =~ ^https://hooks\.slack\.com/services/ ]]; then
      echo "::warning::SLACK_WEBHOOK_URL pode estar malformado"
    fi

# Inserir em um job que roda sempre (ex.: main) após os testes:
- name: Scan script references
  run: |
    chmod +x scripts/ci/scan-script-references.sh
    scripts/ci/scan-script-references.sh

# (Somente na branch main) Rotacionar ledger de uso:
- name: Rotate usage ledger
  if: github.ref == 'refs/heads/main'
  run: |
    source scripts/utils/common.sh
    _btv_rotate_ledger
