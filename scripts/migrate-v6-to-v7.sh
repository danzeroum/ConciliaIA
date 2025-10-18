#!/bin/bash
# BuildToValue v6 to v7 - Migration Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/utils/common.sh"

# Default values
V6_PATH=""
DRY_RUN=false
BACKUP_BEFORE=true
SKIP_VALIDATION=false

show_help() {
  cat << EOF
BuildToValue v6 to v7 - Migration Script

Usage: $0 [OPTIONS]

Options:
  --v6-path PATH         Path to v6 installation (required)
  --dry-run             Simulate migration without changes
  --no-backup           Skip backup before migration
  --skip-validation     Skip v6 validation
  --help                Show this help message

Examples:
  $0 --v6-path=/path/to/v6
  $0 --v6-path=/path/to/v6 --dry-run
  $0 --v6-path=/path/to/v6 --no-backup

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --v6-path)
      V6_PATH="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --no-backup)
      BACKUP_BEFORE=false
      shift
      ;;
    --skip-validation)
      SKIP_VALIDATION=true
      shift
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      log_error "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate v6 path
if [ -z "$V6_PATH" ]; then
  log_error "--v6-path is required"
  show_help
  exit 1
fi

if [ ! -d "$V6_PATH" ]; then
  log_error "v6 path not found: $V6_PATH"
  exit 1
fi

# Migration statistics
declare -A migration_stats
migration_stats[decisions_migrated]=0
migration_stats[lessons_migrated]=0
migration_stats[personas_updated]=0
migration_stats[configs_updated]=0
migration_stats[errors]=0

# Validate v6 installation
validate_v6() {
  log_section "Step 1: Validating v6 Installation"
  
  if [ "$SKIP_VALIDATION" = true ]; then
    log_info "Skipping validation"
    return 0
  fi
  
  # Check for v6 markers
  if [ ! -f "$V6_PATH/.buildtovalue/version" ]; then
    log_error "Not a valid BuildToValue installation"
    return 1
  fi
  
  local v6_version=$(cat "$V6_PATH/.buildtovalue/version" 2>/dev/null)
  if [[ ! "$v6_version" =~ ^6\. ]]; then
    log_error "Not a v6 installation (found: $v6_version)"
    return 1
  fi
  
  log_success "Valid v6 installation found: $v6_version"
  
  # Check components
  local components=(
    ".buildtovalue/consensus"
    ".buildtovalue/ledger"
    ".buildtovalue/squad"
  )
  
  for component in "${components[@]}"; do
    if [ -d "$V6_PATH/$component" ]; then
      log_success "Found: $component"
    else
      log_warn "Missing: $component (will be created)"
    fi
  done
  
  return 0
}

# Backup v6 data
backup_v6() {
  if [ "$BACKUP_BEFORE" != true ]; then
    log_info "Skipping backup"
    return 0
  fi
  
  log_section "Step 2: Backing Up v6 Data"
  
  local backup_file="$PROJECT_ROOT/backups/v6-backup-before-migration-$(date +%Y%m%d-%H%M%S).tar.gz"
  
  mkdir -p "$PROJECT_ROOT/backups"
  
  log_info "Creating backup: $backup_file"
  
  tar czf "$backup_file" -C "$V6_PATH" .buildtovalue
  
  local size=$(du -h "$backup_file" | cut -f1)
  log_success "Backup created: $backup_file ($size)"
  
  echo "$backup_file"
}

# Migrate consensus files
migrate_consensus() {
  log_section "Step 3: Migrating Consensus"
  
  local v6_consensus="$V6_PATH/.buildtovalue/consensus"
  local v7_consensus="$PROJECT_ROOT/.buildtovalue/consensus"
  
  if [ ! -d "$v6_consensus" ]; then
    log_warn "No consensus files found in v6"
    return 0
  fi
  
  mkdir -p "$v7_consensus"
  
  # Find all consensus files
  local consensus_files=$(find "$v6_consensus" -name "*.json" 2>/dev/null)
  
  if [ -z "$consensus_files" ]; then
    log_warn "No consensus files to migrate"
    return 0
  fi
  
  local count=0
  
  for file in $consensus_files; do
    local filename=$(basename "$file")
    local target="$v7_consensus/$filename"
    
    if [ "$DRY_RUN" = true ]; then
      log_info "[DRY RUN] Would migrate: $filename"
    else
      # Read v6 consensus
      local v6_data=$(cat "$file")
      
      # Convert to v7 format (add version field)
      local v7_data=$(echo "$v6_data" | jq '. + {version: "7.0", migrated_from: "v6"}')
      
      # Write to v7
      echo "$v7_data" > "$target"
      
      log_success "Migrated: $filename"
    fi
    
    ((count++))
  done
  
  migration_stats[configs_updated]=$count
  log_success "Migrated $count consensus file(s)"
}

# Migrate decision ledger
migrate_ledger() {
  log_section "Step 4: Migrating Decision Ledger"
  
  local v6_ledger="$V6_PATH/.buildtovalue/ledger"
  local v7_ledger="$PROJECT_ROOT/.buildtovalue/ledger/decisions"
  
  if [ ! -d "$v6_ledger" ]; then
    log_warn "No ledger found in v6"
    return 0
  fi
  
  mkdir -p "$v7_ledger"
  
  # Find all decision files
  local decision_files=$(find "$v6_ledger" -name "*.jsonl" 2>/dev/null)
  
  if [ -z "$decision_files" ]; then
    log_warn "No decisions to migrate"
    return 0
  fi
  
  local total_decisions=0
  local migrated_decisions=0
  
  for file in $decision_files; do
    local filename=$(basename "$file")
    local target="$v7_ledger/$filename"
    
    if [ "$DRY_RUN" = true ]; then
      local line_count=$(wc -l < "$file")
      log_info "[DRY RUN] Would migrate: $filename ($line_count decisions)"
      ((total_decisions += line_count))
      continue
    fi
    
    # Process each decision
    local temp_file=$(mktemp)
    
    while IFS= read -r line; do
      if [ -z "$line" ]; then
        continue
      fi
      
      ((total_decisions++))
      
      # Parse v6 decision
      local v6_decision="$line"
      
      # Convert to v7 format
      local v7_decision=$(echo "$v6_decision" | jq '
        . + {
          version: "7.0",
          migrated_from: "v6",
          routing: (.routing // {}) + {method: "historical"},
          execution: (.execution // {}),
          outcome: (.outcome // {})
        }
      ')
      
      if [ $? -eq 0 ]; then
        echo "$v7_decision" >> "$temp_file"
        ((migrated_decisions++))
      else
        log_warn "Failed to convert decision (line $total_decisions)"
        ((migration_stats[errors]++))
      fi
    done < "$file"
    
    # Move temp file to target
    mv "$temp_file" "$target"
    
    log_success "Migrated: $filename ($migrated_decisions decisions)"
  done
  
  migration_stats[decisions_migrated]=$migrated_decisions
  log_success "Migrated $migrated_decisions/$total_decisions decisions"
}

# Migrate lessons learned
migrate_lessons() {
  log_section "Step 5: Migrating Lessons Learned"
  
  local v6_lessons="$V6_PATH/.buildtovalue/learning/lessons"
  local v7_lessons="$PROJECT_ROOT/.buildtovalue/learning/lessons"
  
  if [ ! -d "$v6_lessons" ]; then
    log_warn "No lessons found in v6"
    return 0
  fi
  
  mkdir -p "$v7_lessons"
  
  # Find all lesson files
  local lesson_files=$(find "$v6_lessons" -name "*.md" 2>/dev/null)
  
  if [ -z "$lesson_files" ]; then
    log_warn "No lessons to migrate"
    return 0
  fi
  
  local count=0
  
  for file in $lesson_files; do
    local filename=$(basename "$file")
    local target="$v7_lessons/$filename"
    
    if [ "$DRY_RUN" = true ]; then
      log_info "[DRY RUN] Would migrate: $filename"
    else
      # Add v7 metadata header if not present
      if ! grep -q "migrated_from: v6" "$file"; then
        {
          echo "---"
          echo "migrated_from: v6"
          echo "migration_date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
          echo "---"
          echo ""
          cat "$file"
        } > "$target"
      else
        cp "$file" "$target"
      fi
      
      log_success "Migrated: $filename"
    fi
    
    ((count++))
  done
  
  migration_stats[lessons_migrated]=$count
  log_success "Migrated $count lesson(s)"
}

# Update persona configurations
update_personas() {
  log_section "Step 6: Updating Persona Configurations"
  
  local v6_personas="$V6_PATH/.buildtovalue/squad/personas"
  local v7_personas="$PROJECT_ROOT/.buildtovalue/squad/personas"
  
  if [ ! -d "$v6_personas" ]; then
    log_warn "No personas found in v6, using v7 defaults"
    return 0
  fi
  
  mkdir -p "$v7_personas"
  
  # v7 has 11 personas, v6 had 7
  local v6_persona_list=(
    "ia-product-manager"
    "ia-arquiteto"
    "ia-developer"
    "ia-qa"
    "ia-ops"
    "ia-auditor"
    "ia-designer"
  )
  
  local count=0
  
  for persona in "${v6_persona_list[@]}"; do
    local v6_file="$v6_personas/${persona}.yaml"
    local v7_file="$v7_personas/${persona}.yaml"
    
    if [ ! -f "$v6_file" ]; then
      continue
    fi
    
    if [ "$DRY_RUN" = true ]; then
      log_info "[DRY RUN] Would update: $persona"
      ((count++))
      continue
    fi
    
    # Read v6 persona
    local v6_config=$(cat "$v6_file")
    
    # Update to v7 format (add new fields)
    echo "$v6_config" | sed 's/version: "6.0"/version: "7.0"/' > "$v7_file"
    
    log_success "Updated: $persona"
    ((count++))
  done
  
  # Note about new personas
  log_info "Note: v7 adds 4 new personas:"
  log_info "  - ia-business-analyst"
  log_info "  - ia-data-architect"
  log_info "  - ia-integration-specialist"
  log_info "  - ia-ethics-guardian"
  
  migration_stats[personas_updated]=$count
  log_success "Updated $count persona(s)"
}

# Migrate to PostgreSQL
migrate_to_postgres() {
  log_section "Step 7: Migrating to PostgreSQL"
  
  if [ "$DRY_RUN" = true ]; then
    log_info "[DRY RUN] Would migrate decisions to PostgreSQL"
    return 0
  fi
  
  # Check if PostgreSQL is running
  if ! docker exec buildtovalue-postgres pg_isready -U btv_user 2>/dev/null; then
    log_error "PostgreSQL is not running"
    log_info "Start services first: docker-compose up -d"
    return 1
  fi
  
  log_info "Importing decisions to PostgreSQL..."
  
  # Use Python script to import
  if [ -f "$SCRIPT_DIR/python/import_to_postgres.py" ]; then
    python3 "$SCRIPT_DIR/python/import_to_postgres.py" \
      --source="$PROJECT_ROOT/.buildtovalue/ledger/decisions" \
      --batch-size=100
  else
    log_warn "import_to_postgres.py not found, skipping database migration"
    log_info "Decisions are available in: .buildtovalue/ledger/decisions"
  fi
  
  log_success "PostgreSQL migration complete"
}

# Create RAG index
create_rag_index() {
  log_section "Step 8: Creating RAG Index"
  
  if [ "$DRY_RUN" = true ]; then
    log_info "[DRY RUN] Would create RAG index"
    return 0
  fi
  
  # Check if ChromaDB is running
  if ! curl -s http://localhost:8000/api/v1/heartbeat >/dev/null 2>&1; then
    log_warn "ChromaDB is not running"
    log_info "Start services first: docker-compose up -d"
    log_info "Then run: ./scripts/learning/create-rag-collection.sh"
    return 0
  fi
  
  log_info "Creating RAG collection..."
  
  if [ -f "$SCRIPT_DIR/learning/create-rag-collection.sh" ]; then
    bash "$SCRIPT_DIR/learning/create-rag-collection.sh"
  else
    log_warn "create-rag-collection.sh not found"
  fi
  
  log_info "Indexing decisions..."
  
  if [ -f "$SCRIPT_DIR/learning/index-decisions.sh" ]; then
    bash "$SCRIPT_DIR/learning/index-decisions.sh" --all
  else
    log_warn "index-decisions.sh not found"
  fi
  
  log_success "RAG index created"
}

# Update configuration
update_configuration() {
  log_section "Step 9: Updating Configuration"
  
  if [ "$DRY_RUN" = true ]; then
    log_info "[DRY RUN] Would update configuration"
    return 0
  fi
  
  # Update version file
  echo "7.0" > "$PROJECT_ROOT/.buildtovalue/version"
  
  # Update foundation config
  local foundation_config="$PROJECT_ROOT/.buildtovalue/config/foundation.yaml"
  
  if [ -f "$foundation_config" ]; then
    # Update version
    sed -i.bak 's/version: "6.0"/version: "7.0"/' "$foundation_config"
    rm -f "$foundation_config.bak"
    
    log_success "Updated foundation.yaml"
  fi
  
  # Add migration metadata
  cat > "$PROJECT_ROOT/.buildtovalue/migration-info.json" << EOF
{
  "migrated_from": "v6",
  "migration_date": "$(timestamp)",
  "v6_path": "$V6_PATH",
  "decisions_migrated": ${migration_stats[decisions_migrated]},
  "lessons_migrated": ${migration_stats[lessons_migrated]},
  "personas_updated": ${migration_stats[personas_updated]}
}
EOF
  
  log_success "Configuration updated"
}

# Display migration summary
display_summary() {
  log_section "Migration Summary"
  
  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}This was a DRY RUN - no changes were made${NC}"
    echo ""
  fi
  
  echo "Statistics:"
  echo "  Decisions migrated:  ${migration_stats[decisions_migrated]}"
  echo "  Lessons migrated:    ${migration_stats[lessons_migrated]}"
  echo "  Personas updated:    ${migration_stats[personas_updated]}"
  echo "  Configs updated:     ${migration_stats[configs_updated]}"
  
  if [ ${migration_stats[errors]} -gt 0 ]; then
    echo -e "  ${RED}Errors:              ${migration_stats[errors]}${NC}"
  fi
  
  echo ""
  
  if [ "$DRY_RUN" = true ]; then
    log_info "Run without --dry-run to perform actual migration"
  else
    log_success "Migration completed successfully!"
    
    echo ""
    echo "Next steps:"
    echo "  1. Verify migration:"
    echo "     ./scripts/troubleshooting/health-check.sh"
    echo ""
    echo "  2. Test routing:"
    echo "     ./scripts/orchestrator/route-problem.sh "test problem""
    echo ""
    echo "  3. Review migrated data:"
    echo "     ./scripts/ledger/list.sh --last=10"
    echo ""
    echo "  4. Optional: Archive v6 installation:"
    echo "     mv $V6_PATH $V6_PATH.archived"
    echo ""
  fi
}

# Main execution
main() {
  log_section "BuildToValue v6 to v7 Migration"
  
  log_info "Source (v6): $V6_PATH"
  log_info "Target (v7): $PROJECT_ROOT"
  
  if [ "$DRY_RUN" = true ]; then
    log_info "Mode: DRY RUN (simulation only)"
  fi
  
  echo ""
  
  local start_time=$(date +%s)
  
  # Validate v6
  if ! validate_v6; then
    error_exit "v6 validation failed"
  fi
  
  # Backup v6
  local backup_file=$(backup_v6)
  
  # Run migration steps
  migrate_consensus
  migrate_ledger
  migrate_lessons
  update_personas
  
  if [ "$DRY_RUN" != true ]; then
    migrate_to_postgres
    create_rag_index
    update_configuration
  fi
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  # Display summary
  display_summary
  
  echo ""
  log_info "Migration took ${duration}s"
  
  if [ -n "$backup_file" ]; then
    echo ""
    log_info "v6 backup saved at: $backup_file"
  fi
}

main "$@"
