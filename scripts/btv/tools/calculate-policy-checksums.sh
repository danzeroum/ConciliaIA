#!/usr/bin/env bash
set -euo pipefail

echo "📋 Checksums de Políticas BuildToValue v7.1"
echo "============================================"
echo ""

if [ -f .buildtovalue/config/governance.yaml ]; then
    GOV_SHA=$(sha1sum .buildtovalue/config/governance.yaml | cut -d' ' -f1)
    echo "governance_yaml: $GOV_SHA"
else
    echo "governance_yaml: (arquivo não encontrado)"
fi

if [ -f .buildtovalue/config/invariants.yaml ]; then
    INV_SHA=$(sha1sum .buildtovalue/config/invariants.yaml | cut -d' ' -f1)
    echo "invariants_yaml: $INV_SHA"
else
    echo "invariants_yaml: (arquivo não encontrado)"
fi

echo ""
echo "💡 Use estes valores no cabeçalho de simulação:"
echo "   policy_checksums:"
echo "     governance_yaml: $GOV_SHA"
echo "     invariants_yaml: $INV_SHA"
