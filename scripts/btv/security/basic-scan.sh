#!/bin/bash
# Stub para scan básico de segurança

set -e

echo "🔒 Running basic security scan..."

# Validações básicas de segurança
echo "📋 Checking for common security issues..."

# 1. Verifica por secrets hardcoded
if grep -r "password.*=.*['\"][^'\"]*['\"]" src/ 2>/dev/null; then
    echo "⚠️  Potential hardcoded passwords found"
else
    echo "✅ No hardcoded passwords detected"
fi

# 2. Verifica dependências conhecidas
if [[ -f "package.json" ]]; then
    if command -v npm >/dev/null 2>&1; then
        npm audit --audit-level moderate || true
    fi
fi

# 3. Verifica permissões de arquivos
find scripts/ -name "*.sh" -exec test -x {} \; -print | while read file; do
    echo "✅ Executable script: $file"
done

echo "✅ Basic security scan completed"
