#!/bin/bash
# BuildToValue v7.0 - RAG Search Test Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../utils/common.sh"

# Default values
QUERY=""
MAX_RESULTS=5
THRESHOLD=0.85
VERBOSE=false

show_help() {
  cat << EOF
BuildToValue v7.0 - RAG Search Test

Usage: $0 [OPTIONS] "QUERY"

Arguments:
  QUERY              Search query (required)

Options:
  --max-results N    Maximum number of results (default: 5)
  --threshold N      Minimum similarity threshold (default: 0.85)
  --verbose          Verbose output
  --help             Show this help message

Examples:
  $0 "how to implement authentication"
  $0 "database optimization" --max-results=10
  $0 "refactoring approach" --threshold=0.90 --verbose

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --max-results)
      MAX_RESULTS="$2"
      shift 2
      ;;
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      if [ -z "$QUERY" ]; then
        QUERY="$1"
      else
        log_error "Unknown option: $1"
        exit 1
      fi
      shift
      ;;
  esac
done

# Validate query
if [ -z "$QUERY" ]; then
  log_error "Query is required"
  show_help
  exit 1
fi

# Check ChromaDB
check_chromadb() {
  log_info "Checking ChromaDB..."
  
  if ! curl -s http://localhost:8000/api/v1/heartbeat >/dev/null 2>&1; then
    log_error "ChromaDB is not running"
    echo ""
    echo "Start ChromaDB:"
    echo "  docker-compose up -d chromadb"
    echo ""
    return 1
  fi
  
  log_success "ChromaDB is running"
  return 0
}

# Perform search
perform_search() {
  log_info "Searching for: \"$QUERY\""
  echo ""
  
  if [ -f "$SCRIPT_DIR/../python/rag_indexer.py" ]; then
    python3 "$SCRIPT_DIR/../python/rag_indexer.py" search \
      --query="$QUERY" \
      --max-results=$MAX_RESULTS \
      --threshold=$THRESHOLD
  else
    log_error "rag_indexer.py not found"
    return 1
  fi
}

# Display search tips
display_tips() {
  if [ "$VERBOSE" = true ]; then
    echo ""
    log_info "Search Tips:"
    echo "  - Use specific technical terms"
    echo "  - Include context (e.g., 'authentication in Spring Boot')"
    echo "  - Try different phrasings if no results"
    echo "  - Lower threshold if too few results"
    echo ""
    echo "Adjust search:"
    echo "  --threshold=0.70  # More results (less strict)"
    echo "  --threshold=0.95  # Fewer results (more strict)"
    echo "  --max-results=20  # More results displayed"
    echo ""
  fi
}

# Main execution
main() {
  log_section "RAG Search Test"
  echo ""
  
  if ! check_chromadb; then
    exit 1
  fi
  
  perform_search
  
  display_tips
}

main "$@"
