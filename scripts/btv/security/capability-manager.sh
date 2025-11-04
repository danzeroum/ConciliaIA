#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Capability Manager
# Auxilia na gestão de Linux capabilities para containers e processos
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso: capability-manager.sh <comando> [opções]

Comandos:
  list <binário>            Lista capabilities associadas a um binário
  add <cap> <binário>       Adiciona capability (setcap)
  drop <cap> <binário>      Remove capability específica
  clear <binário>           Remove todas as capabilities
  profile <nome>            Mostra capabilities sugeridas para perfis (default|strict|permissive)
USAGE
}

ensure_setcap() {
  if ! command -v setcap >/dev/null 2>&1; then
    echo "❌ setcap não disponível. Instale o pacote libcap2-bin." >&2
    exit 1
  fi
}

list_caps() {
  local binary="${1:?Informe o binário}"
  ensure_setcap
  /sbin/getcap "$binary" 2>/dev/null || echo "Nenhuma capability configurada"
}

add_cap() {
  local cap="${1:?Informe a capability}"
  local binary="${2:?Informe o binário}"
  ensure_setcap
  sudo setcap "$cap" "$binary"
  echo "✅ Capability $cap adicionada a $binary"
}

drop_cap() {
  local cap="${1:?Informe a capability}"
  local binary="${2:?Informe o binário}"
  ensure_setcap
  sudo setcap "-r" "$binary" 2>/dev/null || true
  echo "✅ Capability $cap removida de $binary"
}

clear_caps() {
  local binary="${1:?Informe o binário}"
  ensure_setcap
  sudo setcap -r "$binary" 2>/dev/null || true
  echo "✅ Todas as capabilities removidas de $binary"
}

profile_caps() {
  case "${1:-default}" in
    strict)
      echo "strict: cap_net_bind_service"
      ;;
    permissive)
      echo "permissive: cap_net_bind_service, cap_chown, cap_fowner"
      ;;
    *)
      echo "default: nenhuma capability adicional";
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  command="${1:-help}"
  shift || true

  case "$command" in
    list)
      list_caps "$@"
      ;;
    add)
      add_cap "$@"
      ;;
    drop)
      drop_cap "$@"
      ;;
    clear)
      clear_caps "$@"
      ;;
    profile)
      profile_caps "$1"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
fi
