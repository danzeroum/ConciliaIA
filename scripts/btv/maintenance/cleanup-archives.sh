#!/usr/bin/env bash
set -euo pipefail


ARCHIVE_DIR=".buildtovalue/archives"
RETENTION_DAYS="${BTV_RETENTION_DAYS:-90}"
DRY_RUN="${DRY_RUN:-false}"

echo "🧹 Limpeza de archives antigos (retenção: $RETENTION_DAYS dias)"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "⚠️ Modo DRY RUN ativado (nenhum arquivo será removido)"
fi

total_size=0
file_count=0

while IFS= read -r -d '' archive; do
  size=$(stat -c%s "$archive" 2>/dev/null || stat -f%z "$archive")
  total_size=$((total_size + size))
  file_count=$((file_count + 1))

  echo "  📄 $archive ($(numfmt --to=iec-i --suffix=B $size))"

  if [[ "$DRY_RUN" != "true" ]]; then
    rm -f "$archive" "$archive.sha256"
  fi
done < <(find "$ARCHIVE_DIR" -name "ledger-*.jsonl.gz" -type f -mtime +$RETENTION_DAYS -print0)

echo "✅ Total: $file_count arquivos ($(numfmt --to=iec-i --suffix=B $total_size))"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "💡 Execute sem DRY_RUN=true para confirmar remoção"
fi
