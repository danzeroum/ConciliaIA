#!/bin/bash
# BuildToValue v7.1 - IA-Assisted Workflow Manager

set -e

VERSION="1.0.0"
ACTION=$1
PERSONA=$2

# Colors
RED='[0;31m'
GREEN='[0;32m'
YELLOW='[1;33m'
BLUE='[0;34m'
NC='[0m' # No Color

print_usage() {
  cat << EOF
BuildToValue v7.1 - IA-Assisted Workflow Manager

Usage:
  $(basename $0) <action> <persona> [options]

Actions:
  generate      Gera context package para IA externa
  validate      Valida resposta da IA externa
  prepare       Prepara instruções para Codex
  log           Registra decisão no ledger
  recommend     Recomenda melhor IA para tarefa
  help          Mostra esta ajuda

Examples:
  $(basename $0) generate ia-developer "Implementar cache Redis"
  $(basename $0) validate ia-developer response.md
  $(basename $0) prepare response-validated.md
  $(basename $0) log claude "Implementar cache" success 0.92
  $(basename $0) recommend ia-developer implementação

EOF
}

# Validar pré-requisitos
check_prerequisites() {
  local missing=()
  
  command -v jq >/dev/null 2>&1 || missing+=("jq")
  command -v git >/dev/null 2>&1 || missing+=("git")
  
  if [ ${#missing[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${missing[*]}${NC}"
    echo "Install: sudo apt-get install ${missing[*]}"
    exit 1
  fi
}

# Action: generate
action_generate() {
  local persona=$1
  local task=$2
  
  if [ -z "$persona" ] || [ -z "$task" ]; then
    echo -e "${RED}Usage: $(basename $0) generate <persona> "<task>"${NC}"
    exit 1
  fi
  
  echo -e "${BLUE}📦 Generating context package...${NC}"
  echo ""
  
  # Chamar script real
  if [ -f "scripts/orchestrator/generate-context-package.sh" ]; then
    ./scripts/orchestrator/generate-context-package.sh "$persona" "$task"
  else
    echo -e "${YELLOW}⚠️  Script not found, showing manual instructions...${NC}"
    echo ""
    echo "1. Read persona: .buildtovalue/squad/personas/${persona}.yaml"
    echo "2. Read context: README.md, ARCHITECTURE.md"
    echo "3. Read policies: governance.yaml, invariants.yaml"
    echo "4. Generate prompt based on template"
    echo ""
    echo -e "${GREEN}✅ Use IA assistente to simulate this${NC}"
  fi
}

# Action: validate
action_validate() {
  local persona=$1
  local response_file=$2
  
  if [ -z "$persona" ] || [ -z "$response_file" ]; then
    echo -e "${RED}Usage: $(basename $0) validate <persona> <response-file>${NC}"
    exit 1
  fi
  
  if [ ! -f "$response_file" ]; then
    echo -e "${RED}❌ File not found: $response_file${NC}"
    exit 1
  fi
  
  echo -e "${BLUE}🔍 Validating response...${NC}"
  echo ""
  
  # Chamar script real
  if [ -f "scripts/validation/validate-ia-output.sh" ]; then
    ./scripts/validation/validate-ia-output.sh "$response_file" "$persona"
  else
    echo -e "${YELLOW}⚠️  Script not found, showing manual validation...${NC}"
    echo ""
    echo "Validate manually:"
    echo "1. Check BuildToValue-Metadata present"
    echo "2. Check ## Implementação: section"
    echo "3. Check bash instructions present"
    echo "4. Check no dangerous commands"
    echo "5. Check documentation present"
    echo ""
    echo -e "${GREEN}✅ Use IA assistente to simulate this${NC}"
  fi
}

# Action: prepare
action_prepare() {
  local response_file=$1
  
  if [ -z "$response_file" ]; then
    echo -e "${RED}Usage: $(basename $0) prepare <response-file>${NC}"
    exit 1
  fi
  
  if [ ! -f "$response_file" ]; then
    echo -e "${RED}❌ File not found: $response_file${NC}"
    exit 1
  fi
  
  echo -e "${BLUE}🤖 Preparing instructions for Codex...${NC}"
  echo ""
  
  # Extrair instruções bash
  echo "Extracting bash instructions..."
  
  # Procurar seção "Instruções para Codex"
  if grep -q "Instruções para Codex" "$response_file"; then
    # Extrair bloco bash após "Instruções para Codex"
    sed -n '/Instruções para Codex/,/```$/p' "$response_file" |       sed '1d;$d' > /tmp/codex-instructions.sh
    
    echo -e "${GREEN}✅ Instructions extracted to: /tmp/codex-instructions.sh${NC}"
    echo ""
    echo "Preview:"
    head -20 /tmp/codex-instructions.sh
    echo ""
    echo "Full file: cat /tmp/codex-instructions.sh"
  else
    echo -e "${YELLOW}⚠️  'Instruções para Codex' section not found${NC}"
    echo "Ask IA assistente to extract instructions"
  fi
}

# Action: log
action_log() {
  local ia=$1
  local task=$2
  local outcome=$3
  local confidence=$4
  
  if [ -z "$ia" ] || [ -z "$task" ] || [ -z "$outcome" ]; then
    echo -e "${RED}Usage: $(basename $0) log <ia> "<task>" <outcome> [confidence]${NC}"
    exit 1
  fi
  
  confidence=${confidence:-0.90}
  
  echo -e "${BLUE}📝 Logging decision...${NC}"
  
  # Chamar script real
  if [ -f "scripts/ledger/auto-log-decision.sh" ]; then
    ./scripts/ledger/auto-log-decision.sh "$ia" "$task" "$outcome" "$confidence"
  else
    # Fallback manual
    DECISION_ID="DEC-$(date +%Y%m%d-%H%M%S)"
    TIMESTAMP=$(date -Iseconds)
    LEDGER_FILE=".buildtovalue/ledger/decisions/$(date +%Y-%m).jsonl"
    
    mkdir -p "$(dirname "$LEDGER_FILE")"
    
    echo "{"id":"$DECISION_ID","timestamp":"$TIMESTAMP","agent":"$ia","task":"$task","outcome":"$outcome","confidence":$confidence,"automated":false,"source":"ia-assisted"}" >> "$LEDGER_FILE"
    
    echo -e "${GREEN}✅ Decision logged: $DECISION_ID${NC}"
    echo "File: $LEDGER_FILE"
  fi
}

# Action: recommend
action_recommend() {
  local persona=$1
  local task_type=$2
  
  if [ -z "$persona" ]; then
    echo -e "${RED}Usage: $(basename $0) recommend <persona> [task-type]${NC}"
    exit 1
  fi
  
  task_type=${task_type:-"general"}
  
  echo -e "${BLUE}📊 Analyzing IA performance...${NC}"
  echo ""
  
  # Tentar script real
  if [ -f "scripts/analytics/get-best-ia-recommendation.sh" ]; then
    ./scripts/analytics/get-best-ia-recommendation.sh "$persona"
  else
    # Fallback: heurísticas
    echo "Based on general heuristics:"
    echo ""
    echo "For complex implementation:"
    echo "  1. Claude Sonnet (best quality)"
    echo "  2. GPT-4 (alternative)"
    echo ""
    echo "For rapid prototyping:"
    echo "  1. Gemini Flash (fast + free)"
    echo "  2. DeepSeek (free alternative)"
    echo ""
    echo -e "${GREEN}✅ Use IA assistente for data-driven recommendation${NC}"
  fi
}

# Main
main() {
  if [ $# -eq 0 ]; then
    print_usage
    exit 0
  fi
  
  check_prerequisites
  
  case "$ACTION" in
    generate)
      action_generate "$PERSONA" "$3"
      ;;
    validate)
      action_validate "$PERSONA" "$3"
      ;;
    prepare)
      action_prepare "$PERSONA"
      ;;
    log)
      action_log "$PERSONA" "$3" "$4" "$5"
      ;;
    recommend)
      action_recommend "$PERSONA" "$3"
      ;;
    help|--help|-h)
      print_usage
      ;;
    *)
      echo -e "${RED}❌ Unknown action: $ACTION${NC}"
      echo ""
      print_usage
      exit 1
      ;;
  esac
}

main "$@"

