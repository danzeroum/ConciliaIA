#!/usr/bin/env bash
set -euo pipefail

mapfile -t ALL_SCRIPTS < <(git ls-files -- 'scripts/**/*.sh' | sort)

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python - <<'PY' "$TMP/refs.txt"
import pathlib
import re
import sys

output = pathlib.Path(sys.argv[1])
roots = [pathlib.Path(p) for p in ('.github/workflows', 'scripts', 'src')]
pattern = re.compile(r'scripts/[A-Za-z0-9/_\.-]+\.sh')
refs = set()

for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        refs.update(pattern.findall(text))

output.parent.mkdir(parents=True, exist_ok=True)
with output.open('w', encoding='utf-8') as fh:
    for ref in sorted(refs):
        fh.write(ref + '\n')
PY

ALLOW=".buildtovalue/config/scripts-allowlist.txt"
PROTECTED=".buildtovalue/config/scripts-protected.txt"
touch "$ALLOW"
[[ -f "$PROTECTED" ]] || : > "$PROTECTED"

echo "🔎 Referências detectadas:"
cat "$TMP/refs.txt" || true
echo

comm -23 <(printf "%s\n" "${ALL_SCRIPTS[@]}" | sort -u) \
         <(sort -u "$TMP/refs.txt" "$ALLOW") \
  > "$TMP/orphans.txt" || true

echo "🧹 Candidatos à remoção (órfãos):"
cat "$TMP/orphans.txt" || echo "(nenhum)"
echo

if [[ -s "$TMP/orphans.txt" ]]; then
  comm -12 <(sort "$TMP/orphans.txt") <(sort "$PROTECTED") > "$TMP/false_pos.txt" || true
  if [[ -s "$TMP/false_pos.txt" ]]; then
    echo "::error::Scripts órfãos detectados, porém PROTEGIDOS:"
    cat "$TMP/false_pos.txt"
    exit 1
  fi
fi

if [[ -s "$TMP/orphans.txt" ]] && [[ "${STRICT_ORPHANS:-false}" == "true" ]]; then
  echo "::error::Há scripts órfãos não protegidos. Revise a lista acima."
  exit 1
fi
