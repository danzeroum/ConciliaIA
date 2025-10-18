#!/bin/bash
# BuildToValue v7.0 - Route Problem Script
# Routes a problem to the appropriate IA squad

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../utils/common.sh"

PROBLEM=""
CONTEXT_FILE=""
CONTEXT_JSON="{}"
MODE="assisted"
MIN_CONFIDENCE=0.75
MAX_COST=0
USE_CACHE=true
EXECUTE=false
OUTPUT_FORMAT="text"

show_help() {
  cat << 'EOH'
BuildToValue v7.0 - Route Problem

Usage: route-problem.sh [OPTIONS] "PROBLEM_DESCRIPTION"

Arguments:
  PROBLEM_DESCRIPTION    Problem to route (required)

Options:
  --context-file FILE    Path to context file
  --context JSON         JSON context string
  --mode MODE            Routing mode (manual|assisted|autonomous)
  --min-confidence N     Minimum confidence threshold (0.0-1.0)
  --max-cost N           Maximum cost per decision (USD)
  --use-cache BOOL       Use cached decisions (true|false)
  --execute              Execute immediately without confirmation
  --format FORMAT        Output format (text|json)
  --help                 Show this help message
EOH
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --context-file)
      CONTEXT_FILE="$2"
      shift 2
      ;;
    --context)
      CONTEXT_JSON="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --min-confidence)
      MIN_CONFIDENCE="$2"
      shift 2
      ;;
    --max-cost)
      MAX_COST="$2"
      shift 2
      ;;
    --use-cache)
      USE_CACHE="$2"
      shift 2
      ;;
    --execute)
      EXECUTE=true
      shift
      ;;
    --format)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      if [ -z "$PROBLEM" ]; then
        PROBLEM="$1"
        shift
      else
        log_error "Unknown option: $1"
        show_help
        exit 1
      fi
      ;;
  esac
done

if [ -z "$PROBLEM" ]; then
  log_error "Problem description is required"
  show_help
  exit 1
fi

if [ -n "$CONTEXT_FILE" ]; then
  if [ ! -f "$CONTEXT_FILE" ]; then
    log_error "Context file not found: $CONTEXT_FILE"
    exit 1
  fi
  CONTEXT_JSON=$(jq -n --arg content "$(cat "$CONTEXT_FILE")" '{context_file: $content}')
fi

route_problem() {
  local api_url="${API_BASE_URL:-http://localhost:8080}/api/v7/orchestrator/route"

  local payload
  payload=$(jq -n \
    --arg problem "$PROBLEM" \
    --argjson context "$CONTEXT_JSON" \
    --arg mode "$MODE" \
    --argjson min_confidence "$MIN_CONFIDENCE" \
    --argjson max_cost "$MAX_COST" \
    --argjson use_cache "$USE_CACHE" \
    '{
      problem: $problem,
      context: $context,
      options: {
        mode: $mode,
        min_confidence: $min_confidence,
        max_cost: $max_cost,
        use_cache: $use_cache
      }
    }')

  curl -s -X POST "$api_url" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${BUILDTOVALUE_API_KEY:-}" \
    -d "$payload"
}

display_result_text() {
  local result="$1"

  local status
  status=$(echo "$result" | jq -r '.status')
  if [ "$status" != "success" ]; then
    log_error "Routing failed: $(echo "$result" | jq -r '.error.message')"
    exit 1
  fi

  local data
  data=$(echo "$result" | jq '.data')

  echo ""
  log_section "🎯 Routing Analysis Complete"

  echo -e "${CYAN}Problem:${NC} $PROBLEM"
  echo -e "${CYAN}Type:${NC} $(echo "$data" | jq -r '.problem_type')"
  echo -e "${CYAN}Complexity:${NC} $(echo "$data" | jq -r '.complexity')"

  echo ""
  echo -e "${GREEN}Recommended Squad:${NC}"
  local primary_ia
  primary_ia=$(echo "$data" | jq -r '.recommended_squad.primary.ia')
  local primary_conf
  primary_conf=$(echo "$data" | jq -r '.recommended_squad.primary.confidence')
  echo -e "  ${BLUE}Primary:${NC} $primary_ia (confidence: $primary_conf)"

  local support_count
  support_count=$(echo "$data" | jq '.recommended_squad.support | length')
  if [ "$support_count" -gt 0 ]; then
    echo -e "  ${BLUE}Support:${NC}"
    echo "$data" | jq -r '.recommended_squad.support[] | "    - \(.ia) (\(.confidence))"'
  fi

  echo ""
  echo -e "${YELLOW}Suggested Sequence:${NC}"
  echo "$data" | jq -r '.sequence[] | "  \(.step). \(.ia) → \(.task)"'

  echo ""
  local cost duration est_conf
  cost=$(echo "$data" | jq -r '.estimates.cost_usd')
  duration=$(echo "$data" | jq -r '.estimates.duration_hours')
  est_conf=$(echo "$data" | jq -r '.estimates.confidence')
  echo -e "${MAGENTA}Estimates:${NC}"
  echo -e "  Cost: \$$cost"
  echo -e "  Duration: ${duration}h"
  echo -e "  Confidence: ${est_conf}"

  local similar_count
  similar_count=$(echo "$data" | jq '.similar_decisions | length')
  if [ "$similar_count" -gt 0 ]; then
    echo ""
    echo -e "${CYAN}Similar Past Decisions:${NC}"
    echo "$data" | jq -r '.similar_decisions[] | "  - \(.id) (similarity: \(.similarity), outcome: \(.outcome))"'
  fi

  echo ""
}

display_result_json() {
  echo "$1" | jq '.'
}

execute_routing() {
  local result="$1"
  local routing_id
  routing_id=$(echo "$result" | jq -r '.data.routing_id')

  log_info "Executing routing: $routing_id"

  local api_url="${API_BASE_URL:-http://localhost:8080}/api/v7/orchestrator/execute"

  local exec_response
  exec_response=$(curl -s -X POST "$api_url" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${BUILDTOVALUE_API_KEY:-}" \
    -d "{\"routing_id\": \"$routing_id\"}")

  local exec_status
  exec_status=$(echo "$exec_response" | jq -r '.status')
  if [ "$exec_status" != "success" ]; then
    log_error "Execution failed: $(echo "$exec_response" | jq -r '.error.message')"
    return 1
  fi

  local execution_id
  execution_id=$(echo "$exec_response" | jq -r '.data.execution_id')
  log_success "Execution started: $execution_id"

  echo ""
  echo "Track execution:"
  echo "  ./scripts/orchestrator/track-execution.sh $execution_id"
  echo ""
}

main() {
  log_info "Routing problem to squad..."
  echo ""

  local result
  result=$(route_problem)

  if [ "$OUTPUT_FORMAT" = "json" ]; then
    display_result_json "$result"
  else
    display_result_text "$result"
  fi

  if [ "$EXECUTE" = true ]; then
    execute_routing "$result"
    return
  fi

  local confidence
  confidence=$(echo "$result" | jq -r '.data.recommended_squad.primary.confidence')
  if [ -z "$confidence" ] || [ "$confidence" = "null" ]; then
    confidence=0
  fi

  if awk -v conf="$confidence" -v min="$MIN_CONFIDENCE" 'BEGIN {exit !(conf >= min)}'; then
    echo ""
    if confirm "⚡ Execute now?" "n"; then
      execute_routing "$result"
    else
      log_info "Execution cancelled"
      echo ""
      echo "To execute later, run:"
      local routing_id
      routing_id=$(echo "$result" | jq -r '.data.routing_id')
      echo "  ./scripts/orchestrator/execute.sh $routing_id"
    fi
  else
    echo ""
    log_warn "Confidence (${confidence}) below threshold ($MIN_CONFIDENCE)"
    log_info "Consider providing more context or reviewing manually"
  fi
}

main "$@"
