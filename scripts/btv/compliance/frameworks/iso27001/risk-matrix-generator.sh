#!/usr/bin/env bash
# BuildToValue v7.4-Platinum – ISO/IEC 27001: Risk Matrix Generator (wrapper)
# Spec-bound: docs/contracts/compliance/iso27001-contract.yaml
set -euo pipefail

OUT="${1:-risk-matrix.md}"
python3 scripts/compliance/frameworks/iso27001/risk-assessment.py export-matrix --output "${OUT}"
