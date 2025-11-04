#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Span Exporter
# Exporta spans para análise offline
set -euo pipefail

TRACES_DIR="${BTV_TRACES_DIR:-.buildtovalue/telemetry/traces}"
EXPORT_FORMAT="${BTV_EXPORT_FORMAT:-json}"

###############################################################################
# Exporta spans para JSON
###############################################################################
export_spans_json() {
  local output_file="${1:-.buildtovalue/telemetry/spans-export.json}"

  echo "📤 Exportando spans para JSON..."

  if [[ ! -d "$TRACES_DIR" ]]; then
    echo "❌ Diretório de traces não encontrado: $TRACES_DIR" >&2
    return 1
  fi

  if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq não disponível" >&2
    return 1
  fi

  mkdir -p "$(dirname "$output_file")"
  local tmp_file
  tmp_file=$(mktemp)

  shopt -s nullglob
  if [[ $(ls "$TRACES_DIR"/*.json 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "[]" >"$tmp_file"
  else
    jq -s 'add' "$TRACES_DIR"/*.json >"$tmp_file" || echo "[]" >"$tmp_file"
  fi
  shopt -u nullglob

  mv "$tmp_file" "$output_file"

  local span_count
  span_count=$(jq 'length' "$output_file")
  echo "✅ $span_count spans exportados para: $output_file"
}

###############################################################################
# Gera relatório de traces
###############################################################################
generate_trace_report() {
  local spans_file="${1:-.buildtovalue/telemetry/spans-export.json}"

  if [[ ! -f "$spans_file" ]]; then
    echo "❌ Arquivo de spans não encontrado: $spans_file" >&2
    return 1
  fi

  if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq não disponível" >&2
    return 1
  fi

  echo "📊 Relatório de Traces - BuildToValue v7.4"
  echo "=========================================="

  local total_spans
  total_spans=$(jq 'length' "$spans_file")
  echo "Total de spans: $total_spans"

  if [[ "$total_spans" -eq 0 ]]; then
    echo "⚠️ Nenhum span encontrado"
    return 0
  fi

  echo ""
  echo "Spans por operação:"
  jq -r 'group_by(.name) | map({operation: .[0].name, count: length}) | .[] | "  \(.operation): \(.count)"' "$spans_file"

  echo ""
  echo "Duração média por operação (ms):"
  jq -r '
    group_by(.name) |
    map({
      operation: .[0].name,
      avg_duration_ms: (map(.duration_ms) | add / length | floor)
    }) |
    .[] | "  \(.operation): \(.avg_duration_ms)ms"
  ' "$spans_file"

  echo ""
  echo "Spans com erro:"
  local error_count
  error_count=$(jq '[.[] | select(.attributes.error == true)] | length' "$spans_file")
  echo "  Total: $error_count"

  if [[ "$error_count" -gt 0 ]]; then
    echo ""
    echo "Tipos de erro:"
    jq -r '[.[] | select(.attributes.error == true) | .attributes."error.type"] | group_by(.) | map({type: .[0], count: length}) | .[] | "  \(.type): \(.count)"' "$spans_file"
  fi
}

###############################################################################
# Limpa traces antigos
###############################################################################
cleanup_old_traces() {
  local days="${1:-7}"

  echo "🧹 Limpando traces com mais de $days dias..."

  local cleaned=0
  while IFS= read -r -d '' trace_file; do
    rm -f "$trace_file"
    cleaned=$((cleaned + 1))
  done < <(find "$TRACES_DIR" -name "*.json" -type f -mtime +"$days" -print0 2>/dev/null)

  echo "✅ $cleaned arquivos removidos"
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    export)
      export_spans_json "${2:-}"
      ;;
    report)
      generate_trace_report "${2:-}"
      ;;
    cleanup)
      cleanup_old_traces "${2:-7}"
      ;;
    *)
      echo "Uso: $0 {export|report|cleanup} [args]"
      exit 1
      ;;
  esac
fi
