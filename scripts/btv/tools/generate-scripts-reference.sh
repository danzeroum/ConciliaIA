#!/usr/bin/env bash
set -euo pipefail

OUT="SCRIPTS-REFERENCE.md"
echo "# 🔧 Scripts Reference (autogerado)" > "$OUT"
echo "" >> "$OUT"
echo "Gerado em: $(date -Iseconds)" >> "$OUT"
echo "" >> "$OUT"
echo '```' >> "$OUT"
find scripts -type f \( -name "*.sh" -o -name "*.py" \) -print | sort >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"
echo "---" >> "$OUT"
echo "" >> "$OUT"
echo "## Scripts por Categoria" >> "$OUT"
echo "" >> "$OUT"

for dir in scripts/*/; do
    category=$(basename "$dir")
    echo "### $category" >> "$OUT"
    find "$dir" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) -print | sort | while read -r script; do
        script_name=$(basename "$script")
        # Tentar extrair descrição do cabeçalho
        desc=$(head -20 "$script" | grep -E "^#.*Função:|^#.*Purpose:" | head -1 | sed 's/^#[[:space:]]*//' || echo "")
        if [ -n "$desc" ]; then
            echo "- **$script_name**: $desc" >> "$OUT"
        else
            echo "- **$script_name**" >> "$OUT"
        fi
    done
    echo "" >> "$OUT"
done

echo "✅ Referência gerada: $OUT"
