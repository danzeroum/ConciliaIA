#!/bin/bash
# ============================================================
# 🩹 BuildToValue Hotfix – Resolver conflito de dependência httpx
# ============================================================
# Objetivo:
# - Corrigir conflito entre httpx==0.23.3 e httpx>=0.27 identificado nos pipelines
# - Harmonizar versão mínima compatível (>=0.27,<0.29)
# - Seguir política "dependency loosen policy" da BuildToValue v7.1
# ============================================================

set -e

echo "🔧 Aplicando hotfix de dependência httpx..."

FILES=("requirements.txt" "requirements-dev.txt")

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "➡️  Atualizando $file..."
    # Remove linhas antigas
    sed -i '/httpx==/d' "$file" 2>/dev/null || true
    sed -i '/httpx<=/d' "$file" 2>/dev/null || true
    sed -i '/httpx>=/d' "$file" 2>/dev/null || true
    # Adiciona versão harmonizada
    echo "httpx>=0.27,<0.29" >> "$file"
  fi
done

echo "✅ Versão de httpx harmonizada para >=0.27,<0.29"
echo "🧩 Reinstale dependências e reexecute os testes para validar o pipeline."
