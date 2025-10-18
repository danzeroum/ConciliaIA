#!/bin/bash
# BuildToValue v7.0 - Common Utility Functions

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1" >&2
}

log_section() {
  echo ""
  echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
  echo -e "${CYAN}$1${NC}"
  echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
  echo ""
}

# Check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if file exists
file_exists() {
  [ -f "$1" ]
}

# Check if directory exists
dir_exists() {
  [ -d "$1" ]
}

# Wait for condition with timeout
wait_for() {
  local condition="$1"
  local timeout="${2:-30}"
  local interval="${3:-2}"
  local elapsed=0

  while ! eval "$condition" && [ $elapsed -lt $timeout ]; do
    sleep "$interval"
    elapsed=$((elapsed + interval))
  done

  if [ $elapsed -ge $timeout ]; then
    return 1
  fi

  return 0
}

# JSON helper
json_get() {
  local json="$1"
  local key="$2"
  echo "$json" | jq -r "$key"
}

# YAML validator
validate_yaml() {
  local file="$1"

  if ! command_exists yamllint; then
    log_warn "yamllint not installed, skipping YAML validation"
    return 0
  fi

  if yamllint -d relaxed "$file" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Confirm action
confirm() {
  local message="$1"
  local default="${2:-n}"
  local prompt

  if [ "$default" = "y" ]; then
    prompt="[Y/n]"
  else
    prompt="[y/N]"
  fi

  read -p "$message $prompt " response
  response=${response:-$default}

  case "$response" in
    [yY][eE][sS]|[yY])
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Spinner
spinner() {
  local pid=$1
  local delay=0.1
  local spinstr='|/-\\'

  while ps -p $pid > /dev/null 2>&1; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    spinstr=$temp${spinstr%$temp}
    sleep $delay
    printf "\b\b\b\b\b\b"
  done
  printf "    \b\b\b\b"
}

# Progress bar
progress_bar() {
  local current=$1
  local total=$2
  local width=50

  local percent=$((current * 100 / total))
  local filled=$((current * width / total))

  printf "\r["
  printf "%${filled}s" | tr ' ' '█'
  printf "%$((width - filled))s" | tr ' ' '░'
  printf "] %3d%%" "$percent"

  if [ "$current" -eq "$total" ]; then
    echo ""
  fi
}

# Get timestamp
timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Get timestamp (human readable)
timestamp_human() {
  date +"%Y-%m-%d %H:%M:%S"
}

# Check Docker is running
check_docker_running() {
  if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running"
    return 1
  fi
  return 0
}

# Check service is healthy
check_service_healthy() {
  local service="$1"
  local container="${2:-buildtovalue-$service}"

  if docker ps --filter "name=$container" --filter "health=healthy" | grep -q "$container"; then
    return 0
  fi
  return 1
}

# Read JSON config
read_config() {
  local file="$1"
  local key="$2"

  if [ ! -f "$file" ]; then
    log_error "Config file not found: $file"
    return 1
  fi

  jq -r "$key" "$file"
}

# Write JSON config
write_config() {
  local file="$1"
  local key="$2"
  local value="$3"

  local tmp_file=$(mktemp)
  jq "$key = \"$value\"" "$file" > "$tmp_file"
  mv "$tmp_file" "$file"
}

# Backup file
backup_file() {
  local file="$1"
  local backup_dir="${2:-.}"

  if [ -f "$file" ]; then
    local backup_file="$backup_dir/$(basename "$file").backup.$(date +%Y%m%d-%H%M%S)"
    cp "$file" "$backup_file"
    log_info "Backup created: $backup_file"
  fi
}

# Error handler
error_exit() {
  log_error "$1"
  exit "${2:-1}"
}

# Cleanup on exit
cleanup() {
  :
}

trap cleanup EXIT

export -f log_info
export -f log_success
export -f log_warn
export -f log_error
export -f log_section
export -f command_exists
export -f file_exists
export -f dir_exists
export -f wait_for
export -f json_get
export -f validate_yaml
export -f confirm
export -f timestamp
export -f timestamp_human
export -f check_docker_running
export -f check_service_healthy
export -f read_config
export -f write_config
export -f backup_file
export -f error_exit
