#!/usr/bin/env bash

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log_error "Required command '$1' not found"
    exit 1
  fi
}

require_env() {
  local var_name="$1"
  if [[ -z "${!var_name:-}" ]]; then
    log_error "Environment variable '$var_name' is not set"
    exit 1
  fi
}
