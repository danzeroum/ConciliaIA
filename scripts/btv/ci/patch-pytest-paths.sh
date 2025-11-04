#!/usr/bin/env bash
# Ajusta caminhos absolutos para execução de compliance tests
set -euo pipefail
export BTV_REPO_ROOT="$(pwd)"
echo "📁 Patching tests to use absolute repo path: $BTV_REPO_ROOT"
