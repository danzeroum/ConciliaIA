#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Lock Manager
# Gerencia locks distribuídos e limpeza de locks órfãos
set -euo pipefail

# Detecta diretório base relativo ao CWD (para suportar pytest tmp_path)
if [[ -d "$(pwd)/.buildtovalue/locks" ]]; then
  LOCK_DIR="$(pwd)/.buildtovalue/locks"
else
  LOCK_DIR="${BTV_LOCK_DIR:-.buildtovalue/locks}"
fi

MAX_CONCURRENT="${BTV_MAX_CONCURRENT:-5}"
LOCK_TIMEOUT="${BTV_LOCK_TIMEOUT:-300}" # 5 minutos

mkdir -p "$LOCK_DIR"

###############################################################################
# Adquire lock com timeout e suporte a múltiplas instâncias
###############################################################################
acquire_lock() {
  local lock_name="$1"
  local lock_file="$LOCK_DIR/$lock_name.lock"
  local pid_file="$LOCK_DIR/$lock_name.pid"
  local timestamp_file="$LOCK_DIR/$lock_name.ts"

  # Verificar limite de execuções concorrentes
  local active_locks
  active_locks=$(find "$LOCK_DIR" -name "*.lock" -type f 2>/dev/null | wc -l)
  if [[ $active_locks -ge $MAX_CONCURRENT ]]; then
    echo "⚠️ Limite de concorrência atingido: $active_locks/$MAX_CONCURRENT"
    echo "Aguardando slot disponível..."
    local wait_time=0
    while [[ $active_locks -ge $MAX_CONCURRENT ]] && [[ $wait_time -lt $LOCK_TIMEOUT ]]; do
      sleep 2
      wait_time=$((wait_time + 2))
      active_locks=$(find "$LOCK_DIR" -name "*.lock" -type f 2>/dev/null | wc -l)
    done
    if [[ $wait_time -ge $LOCK_TIMEOUT ]]; then
      echo "❌ Timeout aguardando slot de execução"
      return 1
    fi
  fi

  # Criar lock atômico com flock
  exec 200>"$lock_file"
  if ! flock -n 200; then
    if [[ -f "$pid_file" ]]; then
      local old_pid
      old_pid=$(cat "$pid_file")
      if ! kill -0 "$old_pid" 2>/dev/null; then
        echo "⚠️ Lock órfão detectado (PID $old_pid morto). Removendo..."
        release_lock "$lock_name"
        exec 200>"$lock_file"
        flock -n 200 || return 1
      else
        echo "❌ Lock já adquirido por PID $old_pid"
        return 1
      fi
    fi
  fi

  echo "$$" >"$pid_file"
  date -u +"%Y-%m-%dT%H:%M:%SZ" >"$timestamp_file"
  echo "✅ Lock adquirido: $lock_name (PID $$)"
  trap "release_lock '$lock_name'" EXIT INT TERM
}

###############################################################################
# Libera lock e limpa metadados
###############################################################################
release_lock() {
  local lock_name="$1"
  rm -f "$LOCK_DIR/$lock_name.lock" "$LOCK_DIR/$lock_name.pid" "$LOCK_DIR/$lock_name.ts" 2>/dev/null || true
  echo "🔓 Lock liberado: $lock_name"
}

###############################################################################
# Lista locks ativos
###############################################################################
list_locks() {
  echo "🔒 Locks ativos em: $LOCK_DIR"
  shopt -s nullglob
  local locks=("$LOCK_DIR"/*.lock)
  shopt -u nullglob

  if [[ ${#locks[@]} -eq 0 ]]; then
    echo "  - Nenhum lock ativo"
    return 0
  fi

  for lock in "${locks[@]}"; do
    [[ -f "$lock" ]] || continue
    local name pid ts
    name=$(basename "$lock" .lock)
    pid=$(cat "$LOCK_DIR/$name.pid" 2>/dev/null || echo "?")
    ts=$(cat "$LOCK_DIR/$name.ts" 2>/dev/null || echo "unknown")
    echo "  - $name: PID $pid (desde $ts)"
  done
}

###############################################################################
# Limpa locks órfãos - com detecção dinâmica de diretório
###############################################################################
cleanup_orphan_locks() {
  local candidate_dir="$LOCK_DIR"
  if [[ -d "$(pwd)/.buildtovalue/locks" ]]; then
    candidate_dir="$(pwd)/.buildtovalue/locks"
  fi

  echo "🧹 Limpando locks órfãos em: $candidate_dir"
  local cleaned=0

  while IFS= read -r -d '' pid_file; do
    [[ -f "$pid_file" ]] || continue
    local pid lock_name lock_file
    pid=$(cat "$pid_file" 2>/dev/null || echo "")
    lock_name=$(basename "$pid_file" .pid)
    lock_file="$candidate_dir/$lock_name.lock"

    if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
      echo "  ⚠️ Removendo lock órfão: $lock_name (PID $pid morto ou inexistente)"
      rm -f "$lock_file" "$pid_file" "$candidate_dir/$lock_name.ts" 2>/dev/null || true
      cleaned=$((cleaned + 1))
    fi
  done < <(find "$candidate_dir" -maxdepth 1 -name "*.pid" -type f -print0 2>/dev/null)

  echo "✅ $cleaned locks órfãos removidos"
}

###############################################################################
# CLI
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    acquire) acquire_lock "${2:?Lock name required}" ;;
    release) release_lock "${2:?Lock name required}" ;;
    list) list_locks ;;
    cleanup) cleanup_orphan_locks ;;
    *)
      echo "Uso: $0 {acquire|release|list|cleanup} [lock_name]"
      exit 1
      ;;
  esac
fi
