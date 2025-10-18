#!/bin/bash
# BuildToValue v7.0 - Database Backup Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../utils/common.sh"

OUTPUT_DIR="$PROJECT_ROOT/backups"
OUTPUT_FILE=""
COMPRESS=true
INCLUDE_RAG=true
INCLUDE_REDIS=true
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

show_help() {
  cat << 'EOH'
BuildToValue v7.0 - Database Backup

Usage: backup.sh [OPTIONS]

Options:
  --output FILE          Custom output file path
  --output-dir DIR       Output directory (default: backups/)
  --compress BOOL        Compress backup (default: true)
  --include-rag BOOL     Include ChromaDB data (default: true)
  --include-redis BOOL   Include Redis data (default: true)
  --help                 Show this help message
EOH
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --compress)
      COMPRESS="$2"
      shift 2
      ;;
    --include-rag)
      INCLUDE_RAG="$2"
      shift 2
      ;;
    --include-redis)
      INCLUDE_REDIS="$2"
      shift 2
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

mkdir -p "$OUTPUT_DIR"

backup_postgres() {
  log_info "Backing up PostgreSQL..."

  local backup_file="$OUTPUT_DIR/postgres-$TIMESTAMP.sql"
  docker exec buildtovalue-postgres pg_dump -U btv_user buildtovalue > "$backup_file"

  if [ "$COMPRESS" = true ]; then
    gzip "$backup_file"
    backup_file="$backup_file.gz"
  fi

  log_success "PostgreSQL backup: $backup_file"
  echo "$backup_file"
}

backup_chromadb() {
  if [ "$INCLUDE_RAG" != true ]; then
    echo ""
    return
  fi

  log_info "Backing up ChromaDB..."

  local backup_file="$OUTPUT_DIR/chromadb-$TIMESTAMP.tar"
  docker run --rm \
    -v buildtovalue-chromadb-data:/data \
    -v "$OUTPUT_DIR:/backup" \
    alpine tar cf "/backup/chromadb-$TIMESTAMP.tar" -C /data .

  if [ "$COMPRESS" = true ]; then
    gzip "$backup_file"
    backup_file="$backup_file.gz"
  fi

  log_success "ChromaDB backup: $backup_file"
  echo "$backup_file"
}

backup_redis() {
  if [ "$INCLUDE_REDIS" != true ]; then
    echo ""
    return
  fi

  log_info "Backing up Redis..."

  docker exec buildtovalue-redis redis-cli SAVE >/dev/null

  local backup_file="$OUTPUT_DIR/redis-$TIMESTAMP.rdb"
  docker cp buildtovalue-redis:/data/dump.rdb "$backup_file"

  if [ "$COMPRESS" = true ]; then
    gzip "$backup_file"
    backup_file="$backup_file.gz"
  fi

  log_success "Redis backup: $backup_file"
  echo "$backup_file"
}

create_combined_backup() {
  local postgres_backup="$1"
  local chromadb_backup="$2"
  local redis_backup="$3"

  local final_backup
  if [ -n "$OUTPUT_FILE" ]; then
    final_backup="$OUTPUT_FILE"
  else
    final_backup="$OUTPUT_DIR/buildtovalue-backup-$TIMESTAMP.tar.gz"
  fi

  log_info "Creating combined backup..."

  local tar_files=()
  [ -n "$postgres_backup" ] && tar_files+=("$postgres_backup")
  [ -n "$chromadb_backup" ] && tar_files+=("$chromadb_backup")
  [ -n "$redis_backup" ] && tar_files+=("$redis_backup")

  if [ ${#tar_files[@]} -gt 0 ]; then
    local relative_files=()
    for file in "${tar_files[@]}"; do
      relative_files+=("${file#$OUTPUT_DIR/}")
    done
    (cd "$OUTPUT_DIR" && tar czf "$final_backup" "${relative_files[@]}")
  else
    tar czf "$final_backup" --files-from /dev/null
  fi

  for file in "${tar_files[@]}"; do
    rm -f "$file"
  done

  log_success "Combined backup: $final_backup"
  echo "$final_backup"
}

main() {
  log_section "Database Backup"

  if ! check_docker_running; then
    error_exit "Docker is not running"
  fi

  local start_time
  start_time=$(date +%s)

  local postgres_backup chromadb_backup redis_backup
  postgres_backup=$(backup_postgres)
  chromadb_backup=$(backup_chromadb)
  redis_backup=$(backup_redis)

  local final_backup
  final_backup=$(create_combined_backup "$postgres_backup" "$chromadb_backup" "$redis_backup")

  local end_time
  end_time=$(date +%s)
  local duration=$((end_time - start_time))

  echo ""
  log_success "Backup completed in ${duration}s"
  echo ""
  echo "Backup location: $final_backup"
  echo ""
  echo "To restore this backup:"
  echo "  ./scripts/database/restore.sh $final_backup"
  echo ""
}

main "$@"
