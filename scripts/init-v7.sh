#!/bin/bash
# BuildToValue v7.0 - Initialization Script
# Initializes a new BuildToValue v7 project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/utils/common.sh"

show_help() {
  cat << 'EOH'
BuildToValue v7.0 - Initialization Script

Usage: init-v7.sh [OPTIONS]

Options:
  --foundation LEVEL     Set foundation level (lite|standard|enterprise)
                         Default: standard
  --skip-docker          Skip Docker services setup
  --skip-validation      Skip prerequisites validation
  --non-interactive      Run without prompts
  --help                 Show this help message

Examples:
  init-v7.sh                                    # Interactive installation
  init-v7.sh --foundation=lite                  # Lite installation
  init-v7.sh --non-interactive --foundation=enterprise
EOH
}

show_banner() {
  echo -e "${BLUE}"
  cat << 'EOB'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         ██████╗ ██╗   ██╗██╗██╗     ██████╗               ║
║         ██╔══██╗██║   ██║██║██║     ██╔══██╗              ║
║         ██████╔╝██║   ██║██║██║     ██║  ██║              ║
║         ██╔══██╗██║   ██║██║██║     ██║  ██║              ║
║         ██████╔╝╚██████╔╝██║███████╗██████╔╝              ║
║         ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝               ║
║                                                            ║
║              BuildToValue v7.0 - Initialization            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOB
  echo -e "${NC}"
}

validate_prerequisites() {
  log_section "Step 1: Validating Prerequisites"

  local all_ok=true

  if command_exists docker; then
    local docker_version
    docker_version=$(docker --version | grep -oP '\\d+\\.\\d+' | head -1)
    log_success "Docker: $docker_version (required: 20.10+)"
  else
    log_error "Docker: Not installed (required: 20.10+)"
    all_ok=false
  fi

  if command_exists docker-compose; then
    local compose_version
    compose_version=$(docker-compose --version | grep -oP '\\d+\\.\\d+' | head -1)
    log_success "Docker Compose: $compose_version (required: 2.0+)"
  else
    log_error "Docker Compose: Not installed (required: 2.0+)"
    all_ok=false
  fi

  if command_exists git; then
    local git_version
    git_version=$(git --version | grep -oP '\\d+\\.\\d+' | head -1)
    log_success "Git: $git_version (required: 2.30+)"
  else
    log_warn "Git: Not installed (recommended: 2.30+)"
  fi

  local total_mem_gb
  total_mem_gb=$(free -g | awk '/^Mem:/{print $2}')
  if [ "${total_mem_gb:-0}" -ge 8 ]; then
    log_success "RAM: ${total_mem_gb}GB (required: 8GB+)"
  else
    log_warn "RAM: ${total_mem_gb:-unknown}GB (recommended: 8GB+)"
  fi

  local free_disk_gb
  free_disk_gb=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
  if [ "${free_disk_gb:-0}" -ge 20 ]; then
    log_success "Disk Space: ${free_disk_gb}GB available (required: 20GB+)"
  else
    log_warn "Disk Space: ${free_disk_gb:-unknown}GB available (recommended: 20GB+)"
  fi

  if [ "$all_ok" = false ]; then
    log_error "Prerequisites validation failed"
    echo ""
    echo "Please install missing requirements and try again."
    echo "See: https://docs.buildtovalue.com/installation"
    exit 1
  fi

  log_success "All prerequisites validated"
}

create_directory_structure() {
  log_section "Step 2: Creating Directory Structure"

  local dirs=(
    ".buildtovalue/config"
    ".buildtovalue/consensus"
    ".buildtovalue/orchestration/handoff-templates"
    ".buildtovalue/squad/personas"
    ".buildtovalue/learning/rag-index"
    ".buildtovalue/learning/lessons"
    ".buildtovalue/ledger/decisions"
    "docs/ADR"
    "logs"
    "backups"
    "templates"
  )

  for dir in "${dirs[@]}"; do
    if [ ! -d "$PROJECT_ROOT/$dir" ]; then
      mkdir -p "$PROJECT_ROOT/$dir"
      log_info "Created: $dir"
    else
      log_info "Exists: $dir"
    fi
  done

  log_success "Directory structure created"
}

copy_configuration_templates() {
  log_section "Step 3: Copying Configuration Templates"

  if [ ! -f "$PROJECT_ROOT/.env.dev" ] && [ -f "$PROJECT_ROOT/.env.example" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env.dev"
    log_info "Created .env.dev from template"
  elif [ -f "$PROJECT_ROOT/.env.dev" ]; then
    log_info ".env.dev already exists"
  else
    log_warn "No .env.example found. Skipping .env.dev creation."
  fi

  log_info "Generating configuration files..."

  cat > "$PROJECT_ROOT/.buildtovalue/config/foundation.yaml" << EOF_CONF
# BuildToValue v7.0 - Foundation Configuration
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

foundation:
  level: "$FOUNDATION_LEVEL"
  version: "7.0"

  features:
    basic_squad: true
    quality_gates: true
    decision_ledger: true
    full_squad: $( [ "$FOUNDATION_LEVEL" != "lite" ] && echo "true" || echo "false" )
    auto_rag: $( [ "$FOUNDATION_LEVEL" != "lite" ] && echo "true" || echo "false" )
    ml_routing: $( [ "$FOUNDATION_LEVEL" != "lite" ] && echo "true" || echo "false" )
    observability: $( [ "$FOUNDATION_LEVEL" != "lite" ] && echo "true" || echo "false" )
EOF_CONF

  log_success "Configuration files created"
}

PERSONA_LIST=(
  "ia-product-manager"
  "ia-business-analyst"
  "ia-arquiteto"
  "ia-developer"
  "ia-qa"
  "ia-auditor"
  "ia-designer"
  "ia-ops"
  "ia-data-architect"
  "ia-integration-specialist"
  "ia-ethics-guardian"
)

download_persona_templates() {
  log_section "Step 4: Downloading Persona Templates"

  for persona in "${PERSONA_LIST[@]}"; do
    local target_file="$PROJECT_ROOT/.buildtovalue/squad/personas/${persona}.yaml"

    if [ ! -f "$target_file" ]; then
      log_info "Creating: ${persona}.yaml"
      cat > "$target_file" << EOF_PERSONA
persona:
  identity:
    name: "$persona"
    version: "7.0"
    specialization: "AI-powered $persona"
    squad: "technical"

  autonomy:
    current_level: 3

  activation_triggers:
    confidence_threshold: 0.75
EOF_PERSONA
    else
      log_info "Exists: ${persona}.yaml"
    fi
  done

  log_success "Persona templates ready"
}

initialize_docker_services() {
  if [ "$SKIP_DOCKER" = true ]; then
    log_info "Skipping Docker services (--skip-docker flag)"
    return
  fi

  log_section "Step 5: Initializing Docker Services"

  cd "$PROJECT_ROOT"

  if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found"
    exit 1
  fi

  log_info "Starting Docker services..."
  docker-compose up -d

  log_info "Waiting for services to be ready..."

  log_info "Waiting for PostgreSQL..."
  local retries=0
  until docker exec buildtovalue-postgres pg_isready -U btv_user 2>/dev/null || [ $retries -eq 30 ]; do
    sleep 2
    ((retries++))
    echo -n "."
  done
  echo ""

  if [ $retries -eq 30 ]; then
    log_error "PostgreSQL failed to start"
    exit 1
  fi
  log_success "PostgreSQL ready (${retries}s)"

  log_info "Waiting for Redis..."
  retries=0
  until docker exec buildtovalue-redis redis-cli ping 2>/dev/null | grep -q PONG || [ $retries -eq 10 ]; do
    sleep 1
    ((retries++))
    echo -n "."
  done
  echo ""
  log_success "Redis ready (${retries}s)"

  log_info "Waiting for ChromaDB..."
  retries=0
  until curl -s http://localhost:8000/api/v1/heartbeat >/dev/null 2>&1 || [ $retries -eq 15 ]; do
    sleep 2
    ((retries++))
    echo -n "."
  done
  echo ""
  log_success "ChromaDB ready (${retries}s)"

  log_success "All Docker services ready"
}

initialize_database() {
  if [ "$SKIP_DOCKER" = true ]; then
    log_info "Skipping database initialization (--skip-docker flag)"
    return
  fi

  log_section "Step 6: Initializing Database"

  if [ ! -f "$SCRIPT_DIR/database/init-schema.sql" ]; then
    log_warn "init-schema.sql not found, creating basic schema"
    docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue << 'EOF_SQL'
CREATE TABLE IF NOT EXISTS decisions (
  id VARCHAR(50) PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  problem TEXT NOT NULL,
  problem_type VARCHAR(100),
  routing JSONB,
  decision JSONB,
  execution JSONB,
  outcome JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decisions(problem_type);

CREATE TABLE IF NOT EXISTS personas (
  id VARCHAR(100) PRIMARY KEY,
  config JSONB NOT NULL,
  autonomy_level INTEGER DEFAULT 3,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS handoffs (
  id VARCHAR(50) PRIMARY KEY,
  from_ia VARCHAR(100) NOT NULL,
  to_ia VARCHAR(100) NOT NULL,
  status VARCHAR(50),
  artifacts JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
  id SERIAL PRIMARY KEY,
  metric_name VARCHAR(100) NOT NULL,
  metric_value NUMERIC,
  labels JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON metrics(metric_name, timestamp DESC);
EOF_SQL
  else
    docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue < "$SCRIPT_DIR/database/init-schema.sql"
  fi

  log_success "Database initialized"
}

create_initial_consensus() {
  log_section "Step 7: Creating Initial Consensus"

  cat > "$PROJECT_ROOT/.buildtovalue/consensus/discovery-consensus.v7.json" << EOF_CONSENSUS
{
  "version": "7.0",
  "project": {
    "name": "$(basename "$PROJECT_ROOT")",
    "domain": "general",
    "foundation_level": "$FOUNDATION_LEVEL"
  },
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "orchestration": {
    "mode": "assisted",
    "confidence_threshold": 0.75
  },
  "squad": {
    "active_personas": ${#PERSONA_LIST[@]},
    "default_autonomy": 3
  }
}
EOF_CONSENSUS

  log_success "Initial consensus created"
}

run_health_check() {
  log_section "Step 8: Running Health Check"

  if [ -f "$SCRIPT_DIR/troubleshooting/health-check.sh" ]; then
    bash "$SCRIPT_DIR/troubleshooting/health-check.sh" || true
  else
    log_warn "Health check script not found, skipping"
  fi
}

display_next_steps() {
  log_section "🎉 Initialization Complete!"

  echo ""
  echo -e "${GREEN}BuildToValue v7 is ready!${NC}"
  echo ""
  echo "Next steps:"
  echo ""
  echo "  1. Configure your API keys:"
  echo -e "     ${BLUE}nano .env.dev${NC}"
  echo "     Set at least: OPENAI_API_KEY"
  echo ""
  echo "  2. Test the system:"
  echo -e "     ${BLUE}./scripts/orchestrator/route-problem.sh \"How to implement authentication?\"${NC}"
  echo ""
  echo "  3. View dashboard:"
  echo -e "     ${BLUE}./scripts/monitoring/squad-dashboard.sh${NC}"
  echo ""
  echo "  4. Read documentation:"
  echo -e "     ${BLUE}cat docs/GETTING-STARTED.md${NC}"
  echo ""
  echo "Useful commands:"
  echo -e "  Health check:  ${BLUE}./scripts/troubleshooting/health-check.sh${NC}"
  echo -e "  Quality gates: ${BLUE}./scripts/gates-v7.sh --full${NC}"
  echo -e "  Stop services: ${BLUE}docker-compose down${NC}"
  echo -e "  View logs:     ${BLUE}docker-compose logs -f app${NC}"
  echo ""
  echo "Support:"
  echo "  Discord: https://discord.gg/buildtovalue"
  echo "  GitHub:  https://github.com/buildtovalue/v7"
  echo "  Docs:    https://docs.buildtovalue.com"
  echo ""
}

main() {
  FOUNDATION_LEVEL="standard"
  SKIP_DOCKER=false
  SKIP_VALIDATION=false
  INTERACTIVE=true

  while [[ $# -gt 0 ]]; do
    case $1 in
      --foundation)
        FOUNDATION_LEVEL="$2"
        shift 2
        ;;
      --skip-docker)
        SKIP_DOCKER=true
        shift
        ;;
      --skip-validation)
        SKIP_VALIDATION=true
        shift
        ;;
      --non-interactive)
        INTERACTIVE=false
        shift
        ;;
      --help)
        show_help
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
    esac
  done

  show_banner

  log_info "Foundation Level: $FOUNDATION_LEVEL"
  log_info "Project Root: $PROJECT_ROOT"
  echo ""

  if [ "$SKIP_VALIDATION" = false ]; then
    validate_prerequisites
  fi

  create_directory_structure
  copy_configuration_templates
  download_persona_templates
  initialize_docker_services
  initialize_database
  create_initial_consensus

  if [ "$SKIP_DOCKER" = false ]; then
    run_health_check
  fi

  display_next_steps
}

main "$@"
