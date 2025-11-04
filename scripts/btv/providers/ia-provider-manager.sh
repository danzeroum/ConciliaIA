#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - IA Provider Manager
# Gerencia fallback entre múltiplos provedores de IA
set -euo pipefail

WORKDIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PROVIDERS_CONFIG="$WORKDIR/scripts/providers/providers.yaml"
COST_LEDGER="$WORKDIR/.buildtovalue/cost-ledger.jsonl"

mkdir -p "$(dirname "$COST_LEDGER")"

###############################################################################
# Carrega configuração de providers
###############################################################################
load_providers() {
  if ! command -v yq &>/dev/null; then
    echo "⚠️ yq não encontrado. Instale com: pip install yq" >&2
    return 1
  fi
  
  yq -r '.providers[] | select(.enabled == true) | .name' "$PROVIDERS_CONFIG" 2>/dev/null
}

###############################################################################
# Gera código com provider específico
###############################################################################
generate_with_provider() {
  local provider="$1"
  local prompt="$2"
  local model timeout endpoint
  
  # Carregar configurações do provider
  model=$(yq -r ".providers[] | select(.name == \"$provider\") | .models.generation" "$PROVIDERS_CONFIG")
  timeout=$(yq -r ".providers[] | select(.name == \"$provider\") | .timeout" "$PROVIDERS_CONFIG")
  endpoint=$(yq -r ".providers[] | select(.name == \"$provider\") | .endpoint" "$PROVIDERS_CONFIG")
  
  local start_time=$(date +%s)
  local success=false
  local output=""
  local cost=0
  
  case "$provider" in
    ollama)
      if command -v ollama &>/dev/null; then
        output=$(timeout "$timeout" ollama run "$model" "$prompt" 2>&1) && success=true
      fi
      ;;
      
    openai)
      if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        output=$(timeout "$timeout" curl -s "$endpoint/chat/completions" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $OPENAI_API_KEY" \
          -d "{
            \"model\": \"$model\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}],
            \"max_tokens\": 2000
          }" 2>&1) && success=true
        
        # Extrair resposta e calcular custo
        output=$(echo "$output" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$output")
        local tokens=$(echo "$output" | jq -r '.usage.total_tokens // 0' 2>/dev/null || echo "0")
        cost=$(awk "BEGIN {printf \"%.4f\", ($tokens / 1000) * 0.03}")
      fi
      ;;
      
    anthropic)
      if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        output=$(timeout "$timeout" curl -s "$endpoint/messages" \
          -H "content-type: application/json" \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -d "{
            \"model\": \"$model\",
            \"max_tokens\": 2000,
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}]
          }" 2>&1) && success=true
        
        # Extrair resposta e calcular custo
        output=$(echo "$output" | jq -r '.content[0].text' 2>/dev/null || echo "$output")
        local tokens=$(echo "$output" | jq -r '.usage.input_tokens + .usage.output_tokens // 0' 2>/dev/null || echo "0")
        cost=$(awk "BEGIN {printf \"%.4f\", ($tokens / 1000) * 0.015}")
      fi
      ;;
      
    *)
      echo "❌ Provider desconhecido: $provider" >&2
      return 1
      ;;
  esac
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  # Registrar uso no cost ledger
  log_provider_usage "$provider" "$success" "$duration" "$cost"
  
  if [[ "$success" == "true" ]]; then
    echo "$output"
    return 0
  else
    echo "❌ Falha ao gerar com $provider" >&2
    return 1
  fi
}

###############################################################################
# Auditoria com provider específico
###############################################################################
audit_with_provider() {
  local content="$1"
  local provider="${BTV_AUDIT_PROVIDER:-ollama}"
  
  local audit_prompt="Revise o seguinte código gerado por IA e identifique problemas de segurança, qualidade ou ética:\n\n$content"
  
  generate_with_provider "$provider" "$audit_prompt"
}

###############################################################################
# Fallback automático entre providers
###############################################################################
generate_with_fallback() {
  local prompt="$1"
  local max_retries=3
  local backoff=5
  
  # Obter lista de providers ordenados por prioridade
  local providers=($(yq -r '.providers[] | select(.enabled == true) | .name' "$PROVIDERS_CONFIG" | sort))
  
  for provider in "${providers[@]}"; do
    echo "🔄 Tentando provider: $provider" >&2
    
    local retry=0
    while [[ $retry -lt $max_retries ]]; do
      if generate_with_provider "$provider" "$prompt"; then
        echo "✅ Sucesso com provider: $provider" >&2
        return 0
      fi
      
      retry=$((retry + 1))
      if [[ $retry -lt $max_retries ]]; then
        echo "⚠️ Retry $retry/$max_retries para $provider (aguardando ${backoff}s)" >&2
        sleep "$backoff"
      fi
    done
    
    echo "❌ Provider $provider falhou após $max_retries tentativas" >&2
  done
  
  echo "❌ Todos os providers falharam" >&2
  return 1
}

###############################################################################
# Log de uso de provider
###############################################################################
log_provider_usage() {
  local provider="$1"
  local success="$2"
  local duration="$3"
  local cost="${4:-0}"
  
  local entry=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg provider "$provider" \
    --arg success "$success" \
    --arg duration "$duration" \
    --arg cost "$cost" \
    '{
      timestamp: $ts,
      provider: $provider,
      success: ($success == "true"),
      duration_seconds: ($duration | tonumber),
      cost_usd: ($cost | tonumber)
    }'
  )
  
  echo "$entry" >> "$COST_LEDGER"
  
  # Verificar threshold de custo
  check_cost_threshold
}

###############################################################################
# Verifica threshold de custo
###############################################################################
check_cost_threshold() {
  local threshold=$(yq -r '.cost_tracking.alert_threshold_usd' "$PROVIDERS_CONFIG" 2>/dev/null || echo "10.0")
  local total_cost=$(jq -s 'map(.cost_usd) | add' "$COST_LEDGER" 2>/dev/null || echo "0")
  
  if (( $(echo "$total_cost > $threshold" | bc -l) )); then
    echo "⚠️ ALERTA DE CUSTO: Total acumulado \$${total_cost} excede threshold \$${threshold}" >&2
    
    # Enviar notificação (se configurado)
    if command -v notify-send &>/dev/null; then
      notify-send "BuildToValue Cost Alert" "Custo acumulado: \$${total_cost}"
    fi
  fi
}

###############################################################################
# Relatório de custos
###############################################################################
cost_report() {
  echo "💰 BuildToValue - Relatório de Custos"
  echo "====================================="
  
  if [[ ! -f "$COST_LEDGER" ]]; then
    echo "⚠️ Nenhum dado de custo disponível"
    return
  fi
  
  echo ""
  echo "📊 Custos por Provider:"
  jq -r 'group_by(.provider) | map({
    provider: .[0].provider,
    total_cost: (map(.cost_usd) | add),
    requests: length,
    avg_cost: (map(.cost_usd) | add / length)
  }) | .[] | "  \(.provider): $\(.total_cost) (\(.requests) requests, avg $\(.avg_cost))"' "$COST_LEDGER"
  
  echo ""
  echo "📈 Estatísticas Gerais:"
  local total=$(jq -s 'map(.cost_usd) | add' "$COST_LEDGER")
  local count=$(jq -s 'length' "$COST_LEDGER")
  local avg=$(awk "BEGIN {printf \"%.4f\", $total / $count}")
  
  echo "  Total gasto: \$${total}"
  echo "  Total de requests: $count"
  echo "  Custo médio: \$${avg}"
  
  local threshold=$(yq -r '.cost_tracking.alert_threshold_usd' "$PROVIDERS_CONFIG")
  local remaining=$(awk "BEGIN {printf \"%.2f\", $threshold - $total}")
  echo "  Margem restante: \$${remaining} (threshold: \$${threshold})"
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    generate)
      generate_with_fallback "${2:?Prompt required}"
      ;;
    audit)
      audit_with_provider "${2:?Content required}"
      ;;
    cost-report)
      cost_report
      ;;
    list-providers)
      load_providers
      ;;
    *)
      echo "Uso: $0 {generate|audit|cost-report|list-providers} [args]"
      exit 1
      ;;
  esac
fi