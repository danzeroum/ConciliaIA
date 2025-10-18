#!/bin/bash
# BuildToValue v7.0 - Persona Validation Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../utils/common.sh"

# Default values
PERSONA_ID=""
STRICT=false
FIX_ISSUES=false

show_help() {
  cat << EOF
BuildToValue v7.0 - Persona Validation

Usage: $0 [OPTIONS]

Options:
  --ia PERSONA_ID     Validate specific persona (optional)
  --strict           Strict validation (fail on warnings)
  --fix              Attempt to fix issues automatically
  --help             Show this help message

Examples:
  $0                           # Validate all personas
  $0 --ia=ia-developer         # Validate specific persona
  $0 --strict                  # Strict validation
  $0 --ia=ia-developer --fix   # Validate and fix

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --ia|--persona)
      PERSONA_ID="$2"
      shift 2
      ;;
    --strict)
      STRICT=true
      shift
      ;;
    --fix)
      FIX_ISSUES=true
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

# Validation results
declare -A validation_results
total_personas=0
valid_personas=0
invalid_personas=0
warnings=0

# Validate single persona
validate_persona() {
  local persona_file="$1"
  local persona_id=$(basename "$persona_file" .yaml)
  
  ((total_personas++))
  
  log_info "Validating: $persona_id"
  
  local has_errors=false
  local has_warnings=false
  
  # Check file exists
  if [ ! -f "$persona_file" ]; then
    log_error "  File not found"
    validation_results["$persona_id"]="missing"
    ((invalid_personas++))
    return 1
  fi
  
  # Check YAML syntax
  if ! validate_yaml "$persona_file"; then
    log_error "  Invalid YAML syntax"
    validation_results["$persona_id"]="invalid_yaml"
    ((invalid_personas++))
    
    if [ "$FIX_ISSUES" = true ]; then
      log_info "  Attempting to fix YAML..."
    fi
    
    return 1
  fi
  
  # Check required fields
  local required_fields=(
    ".persona.identity.name"
    ".persona.identity.version"
    ".persona.autonomy.current_level"
  )
  
  for field in "${required_fields[@]}"; do
    local value=$(yq eval "$field" "$persona_file" 2>/dev/null)
    
    if [ "$value" = "null" ] || [ -z "$value" ]; then
      log_error "  Missing required field: $field"
      has_errors=true
    fi
  done
  
  # Check version
  local version=$(yq eval '.persona.identity.version' "$persona_file" 2>/dev/null)
  if [ "$version" != "7.0" ]; then
    log_warn "  Incorrect version: $version (expected: 7.0)"
    has_warnings=true
    ((warnings++))
    
    if [ "$FIX_ISSUES" = true ]; then
      log_info "  Fixing version..."
      yq eval '.persona.identity.version = "7.0"' -i "$persona_file"
    fi
  fi
  
  # Check autonomy level
  local autonomy=$(yq eval '.persona.autonomy.current_level' "$persona_file" 2>/dev/null)
  if [ "$autonomy" -lt 1 ] || [ "$autonomy" -gt 5 ]; then
    log_error "  Invalid autonomy level: $autonomy (must be 1-5)"
    has_errors=true
  fi
  
  # Check activation triggers
  local triggers=$(yq eval '.persona.activation_triggers' "$persona_file" 2>/dev/null)
  if [ "$triggers" = "null" ]; then
    log_warn "  No activation triggers defined"
    has_warnings=true
    ((warnings++))
  fi
  
  # Determine result
  if [ "$has_errors" = true ]; then
    validation_results["$persona_id"]="invalid"
    ((invalid_personas++))
    log_error "  Validation FAILED"
    return 1
  elif [ "$has_warnings" = true ] && [ "$STRICT" = true ]; then
    validation_results["$persona_id"]="warning"
    ((invalid_personas++))
    log_warn "  Validation FAILED (strict mode)"
    return 1
  else
    validation_results["$persona_id"]="valid"
    ((valid_personas++))
    log_success "  Validation PASSED"
    return 0
  fi
}

# Validate all personas
validate_all_personas() {
  local personas_dir="$PROJECT_ROOT/.buildtovalue/squad/personas"
  
  if [ ! -d "$personas_dir" ]; then
    log_error "Personas directory not found: $personas_dir"
    return 1
  fi
  
  local persona_files=$(find "$personas_dir" -name "*.yaml" | sort)
  
  if [ -z "$persona_files" ]; then
    log_error "No persona files found"
    return 1
  fi
  
  for file in $persona_files; do
    validate_persona "$file"
    echo ""
  done
}

# Display summary
display_summary() {
  log_section "Validation Summary"
  
  echo "Total personas:  $total_personas"
  echo -e "${GREEN}Valid:${NC}           $valid_personas"
  
  if [ $invalid_personas -gt 0 ]; then
    echo -e "${RED}Invalid:${NC}         $invalid_personas"
  fi
  
  if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Warnings:${NC}        $warnings"
  fi
  
  echo ""
  
  if [ $invalid_personas -gt 0 ]; then
    echo "Invalid personas:"
    for persona in "${!validation_results[@]}"; do
      if [ "${validation_results[$persona]}" != "valid" ]; then
        echo "  - $persona (${validation_results[$persona]})"
      fi
    done
    echo ""
  fi
  
  if [ $invalid_personas -eq 0 ]; then
    if [ "$STRICT" = true ] && [ $warnings -gt 0 ]; then
      log_warn "Validation PASSED with warnings (strict mode enabled)"
      return 1
    else
      log_success "All personas valid ✅"
      return 0
    fi
  else
    log_error "Validation FAILED ❌"
    return 1
  fi
}

# Main execution
main() {
  log_section "Persona Validation"
  echo ""
  
  if [ -n "$PERSONA_ID" ]; then
    local persona_file="$PROJECT_ROOT/.buildtovalue/squad/personas/${PERSONA_ID}.yaml"
    validate_persona "$persona_file"
  else
    validate_all_personas
  fi
  
  local exit_code
  display_summary || exit_code=$?
  exit_code=${exit_code:-0}
  
  exit $exit_code
}

main "$@"
