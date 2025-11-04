#!/usr/bin/env bash
# BuildToValue v7.4-Platinum – Certification Packager
set -euo pipefail

ROOT="."
OUT_DIR="${ROOT}/.buildtovalue/compliance/certification-packages"
REP_DIR="${ROOT}/.buildtovalue/compliance"
mkdir -p "${OUT_DIR}"

collect() {
  local fw="$1"
  case "${fw}" in
    gdpr)
      tar -czf "${OUT_DIR}/gdpr-certification.tar.gz" \
        -C "${ROOT}" docs/contracts/compliance/gdpr-contract.yaml \
        -C "${ROOT}" .buildtovalue/compliance/gdpr-data-inventory.json \
        -C "${ROOT}" .buildtovalue/compliance/gdpr-dpia-report.json
      ;;
    sox)
      tar -czf "${OUT_DIR}/sox-certification.tar.gz" \
        -C "${ROOT}" docs/contracts/compliance/sox-contract.yaml \
        -C "${ROOT}" .buildtovalue/compliance/reports
      ;;
    iso27001)
      tar -czf "${OUT_DIR}/iso27001-certification.tar.gz" \
        -C "${ROOT}" docs/contracts/compliance/iso27001-contract.yaml \
        -C "${ROOT}" .buildtovalue/compliance/iso27001-risk-register.json
      ;;
    all)
      collect gdpr; collect sox; collect iso27001
      tar -czf "${OUT_DIR}/unified-certification.tar.gz" -C "${OUT_DIR}" .
      ;;
    *) echo "Uso: $0 collect {gdpr|sox|iso27001|all} | validate"; exit 2 ;;
  esac
  echo "✅ Package created (${fw}) → ${OUT_DIR}"
}

validate() {
  # Validação leve: os arquivos existem e são tar.gz
  ls -l "${OUT_DIR}"/*.tar.gz
  echo "✅ Packages validated."
}

case "${1:-help}" in
  collect) collect "${2:?framework}" ;;
  validate) validate ;;
  *) echo "Uso: $0 collect {gdpr|sox|iso27001|all} | validate"; exit 2 ;;
esac
