#!/bin/bash
# BuildToValue v7.0 - Database Restore Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../utils/common.sh"

# Default values
BACKUP_FILE=""
FORCE=false
SKIP_VALIDATION=false

show_help() {
  cat << EOF
BuildToValue v7.0 - Database Restore

Usage: $0 [OPTIONS] BACKUP_FILE

Arguments:
  BACKUP_FILE    Path to backup file (.tar.gz)

Options:
  --force              Skip confirmation prompts
  --skip-validation    Skip backup validation
  --help              Show this help message

Examples:
  $0 backups/buildtovalue-backup-20250120.tar.gz
  $0 --force backup.tar.gz

WARNING: This will overwrite all existing data!

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      FORCE=true
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
      if [ -z "$BACKUP_FILE" ]; then
        BACKUP_FILE="$1"
      else
        log_error "Unknown option: $1"
        exit 1
      fi
      shift
      ;;
  esac
done

# Validate backup file
if [ -z "$BACKUP_FILE" ]; then
  log_error "Backup file is required"
  show_help
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  log_error "Backup file not found: $BACKUP_FILE"
  exit 1
fi

# Extract backup
extract_backup() {
  log_info "Extracting backup..."
  
  local extract_dir="$PROJECT_ROOT/backups/.restore-temp"
  mkdir -p "$extract_dir"
  
  tar xzf "$BACKUP_FILE" -C "$extract_dir"
  
  log_success "Backup extracted to: $extract_dir"
  echo "$extract_dir"
}

# Validate backup contents
validate_backup() {
  local extract_dir="$1"
  
  if [ "$SKIP_VALIDATION" = true ]; then
    log_info "Skipping validation"
    return 0
  fi
  
  log_info "Validating backup contents..."
  
  local postgres_backup=$(find "$extract_dir" -name "postgres-*.sql.gz" | head -1)
  
  if [ -z "$postgres_backup" ]; then
    log_error "PostgreSQL backup not found in archive"
    return 1
  fi
  
  log_success "Validation passed"
  return 0
}

# Stop services
stop_services() {
  log_info "Stopping services..."
  
  cd "$PROJECT_ROOT"
  docker-compose stop app
  
  log_success "Services stopped"
}

# Restore PostgreSQL
restore_postgres() {
  local extract_dir="$1"
  
  log_info "Restoring PostgreSQL..."
  
  local postgres_backup=$(find "$extract_dir" -name "postgres-*.sql.gz" | head -1)
  
  if [ -z "$postgres_backup" ]; then
    log_error "PostgreSQL backup not found"
    return 1
  fi
  
  # Drop existing database
  log_warn "Dropping existing database..."
  docker exec buildtovalue-postgres psql -U postgres -c "DROP DATABASE IF EXISTS buildtovalue;" 2>/dev/null || true
  
  # Create fresh database
  docker exec buildtovalue-postgres psql -U postgres -c "CREATE DATABASE buildtovalue OWNER btv_user;"
  
  # Restore from backup
  gunzip -c "$postgres_backup" | docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue
  
  log_success "PostgreSQL restored"
}

# Restore ChromaDB
restore_chromadb() {
  local extract_dir="$1"
  
  local chromadb_backup=$(find "$extract_dir" -name "chromadb-*.tar.gz" | head -1)
  
  if [ -z "$chromadb_backup" ]; then
    log_warn "ChromaDB backup not found, skipping"
    return 0
  fi
  
  log_info "Restoring ChromaDB..."
  
  # Stop ChromaDB
  docker-compose stop chromadb
  
  # Remove old data
  docker volume rm buildtovalue-chromadb-data 2>/dev/null || true
  
  # Create new volume
  docker volume create buildtovalue-chromadb-data
  
  # Restore data
  docker run --rm \
    -v buildtovalue-chromadb-data:/data \
    -v "$extract_dir:/backup" \
    alpine sh -c "cd /data && tar xzf /backup/$(basename "$chromadb_backup")"
  
  # Start ChromaDB
  docker-compose up -d chromadb
  
  # Wait for it to be ready
  log_info "Waiting for ChromaDB..."
  local retries=0
  until curl -s http://localhost:8000/api/v1/heartbeat >/dev/null 2>&1 || [ $retries -eq 15 ]; do
    sleep 2
    ((retries++))
  done
  
  log_success "ChromaDB restored"
}

# Restore Redis
restore_redis() {
  local extract_dir="$1"
  
  local redis_backup=$(find "$extract_dir" -name "redis-*.rdb.gz" | head -1)
  
  if [ -z "$redis_backup" ]; then
    log_warn "Redis backup not found, skipping"
    return 0
  fi
  
  log_info "Restoring Redis..."
  
  # Stop Redis
  docker-compose stop redis
  
  # Restore RDB file
  gunzip -c "$redis_backup" > "$PROJECT_ROOT/backups/.restore-temp/dump.rdb"
  docker cp "$PROJECT_ROOT/backups/.restore-temp/dump.rdb" buildtovalue-redis:/data/dump.rdb
  
  # Start Redis
  docker-compose up -d redis
  
  # Wait for it to be ready
  log_info "Waiting for Redis..."
  local retries=0
  until docker exec buildtovalue-redis redis-cli ping 2>/dev/null | grep -q PONG || [ $retries -eq 10 ]; do
    sleep 1
    ((retries++))
  done
  
  log_success "Redis restored"
}

# Start services
start_services() {
  log_info "Starting services..."
  
  cd "$PROJECT_ROOT"
  docker-compose up -d
  
  # Wait for application
  log_info "Waiting for application..."
  local retries=0
  until curl -s http://localhost:8080/api/v7/health >/dev/null 2>&1 || [ $retries -eq 30 ]; do
    sleep 2
    ((retries++))
    echo -n "."
  done
  echo ""
  
  log_success "Services started"
}

# Verify restoration
verify_restoration() {
  log_info "Verifying restoration..."
  
  # Check database
  local decision_count=$(docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -tAc \
    "SELECT COUNT(*) FROM decisions;" 2>/dev/null)
  
  if [ -n "$decision_count" ]; then
    log_success "Database: $decision_count decisions found"
  else
    log_warn "Database: Could not verify"
  fi
  
  # Check personas
  local persona_count=$(docker exec buildtovalue-postgres psql -U btv_user -d buildtovalue -tAc \
    "SELECT COUNT(*) FROM personas;" 2>/dev/null)
  
  if [ -n "$persona_count" ]; then
    log_success "Personas: $persona_count found"
  else
    log_warn "Personas: Could not verify"
  fi
}

# Cleanup
cleanup() {
  log_info "Cleaning up..."
  
  local extract_dir="$PROJECT_ROOT/backups/.restore-temp"
  if [ -d "$extract_dir" ]; then
    rm -rf "$extract_dir"
  fi
  
  log_success "Cleanup complete"
}

# Main execution
main() {
  log_section "Database Restore"
  
  # Check Docker is running
  if ! check_docker_running; then
    error_exit "Docker is not running"
  fi
  
  # Display backup info
  local backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
  log_info "Backup file: $BACKUP_FILE"
  log_info "Backup size: $backup_size"
  echo ""
  
  # Warning
  log_warn "⚠️  WARNING ⚠️"
  echo ""
  echo "This will:"
  echo "  1. Stop all services"
  echo "  2. DROP the existing database"
  echo "  3. Restore from backup"
  echo "  4. Overwrite all current data"
  echo ""
  
  if [ "$FORCE" != true ]; then
    if ! confirm "Are you sure you want to continue?"; then
      log_info "Restore cancelled"
      exit 0
    fi
    
    echo ""
    if ! confirm "Really sure? This cannot be undone!"; then
      log_info "Restore cancelled"
      exit 0
    fi
  fi
  
  echo ""
  local start_time=$(date +%s)
  
  # Extract backup
  local extract_dir=$(extract_backup)
  
  # Validate backup
  if ! validate_backup "$extract_dir"; then
    cleanup
    error_exit "Backup validation failed"
  fi
  
  # Stop services
  stop_services
  
  # Restore components
  restore_postgres "$extract_dir"
  restore_chromadb "$extract_dir"
  restore_redis "$extract_dir"
  
  # Start services
  start_services
  
  # Verify
  verify_restoration
  
  # Cleanup
  cleanup
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  echo ""
  log_success "Restore completed in ${duration}s"
  echo ""
  echo "Next steps:"
  echo "  1. Run health check: ./scripts/troubleshooting/health-check.sh"
  echo "  2. Verify data: ./scripts/ledger/list.sh"
  echo "  3. Test routing: ./scripts/orchestrator/route-problem.sh ""test"""
  echo ""
}

main "$@"
