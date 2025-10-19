#!/usr/bin/env bash

log_section() {
  printf '\n\033[1;34m==> %s\033[0m\n' "$1"
}

log_info() {
  printf '\033[0;36m[INFO]\033[0m %s\n' "$1"
}

log_success() {
  printf '\033[0;32m[SUCCESS]\033[0m %s\n' "$1"
}

log_warn() {
  printf '\033[0;33m[WARN]\033[0m %s\n' "$1"
}

log_error() {
  printf '\033[0;31m[ERROR]\033[0m %s\n' "$1" >&2
}
