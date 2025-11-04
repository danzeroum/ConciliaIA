#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - Resource Limiter
# Aplica limits de CPU, memória, I/O e disco
set -euo pipefail

###############################################################################
# Configurações padrão
###############################################################################
DEFAULT_MEMORY_MB="${BTV_MEMORY_LIMIT_MB:-512}"
DEFAULT_MEMORY_SWAP_MB="${BTV_MEMORY_SWAP_MB:-512}"
DEFAULT_CPU_SHARES="${BTV_CPU_SHARES:-1024}"
DEFAULT_CPU_QUOTA="${BTV_CPU_QUOTA:-100000}"
DEFAULT_CPU_PERIOD="${BTV_CPU_PERIOD:-100000}"
DEFAULT_PIDS_LIMIT="${BTV_PIDS_LIMIT:-100}"
DEFAULT_IO_WEIGHT="${BTV_IO_WEIGHT:-500}"
DEFAULT_DISK_QUOTA_MB="${BTV_DISK_QUOTA_MB:-1024}"

###############################################################################
# Aplica resource limits via Docker
###############################################################################
apply_docker_limits() {
  local container_name="${1:?Container name required}"
  local profile="${2:-default}"

  local memory_mb="$DEFAULT_MEMORY_MB"
  local memory_swap_mb="$DEFAULT_MEMORY_SWAP_MB"
  local cpu_quota="$DEFAULT_CPU_QUOTA"
  local pids_limit="$DEFAULT_PIDS_LIMIT"

  case "$profile" in
    strict)
      memory_mb=256
      memory_swap_mb=256
      cpu_quota=50000
      pids_limit=50
      ;;
    permissive)
      memory_mb=1024
      memory_swap_mb=1024
      cpu_quota=200000
      pids_limit=200
      ;;
  esac

  local docker_limits=(
    "--memory=${memory_mb}m"
    "--memory-swap=${memory_swap_mb}m"
    "--cpu-shares=$DEFAULT_CPU_SHARES"
    "--cpu-quota=$cpu_quota"
    "--cpu-period=$DEFAULT_CPU_PERIOD"
    "--pids-limit=$pids_limit"
    "--blkio-weight=$DEFAULT_IO_WEIGHT"
    "--ulimit"
    "nofile=1024:1024"
    "--ulimit"
    "nproc=100:100"
  )

  printf '%s ' "${docker_limits[@]}"
}

###############################################################################
# Aplica resource limits via cgroups v2 (fallback nativo)
###############################################################################
apply_cgroup_limits() {
  local pid="${1:?PID required}"
  local profile="${2:-default}"

  if [[ ! -d /sys/fs/cgroup ]]; then
    echo "⚠️ cgroups v2 não disponível" >&2
    return 1
  fi

  local cgroup_path="/sys/fs/cgroup/buildtovalue/task-$pid"

  sudo mkdir -p "$cgroup_path"

  local memory_mb="$DEFAULT_MEMORY_MB"
  local cpu_quota="$DEFAULT_CPU_QUOTA"
  local cpu_period="$DEFAULT_CPU_PERIOD"
  local pids_limit="$DEFAULT_PIDS_LIMIT"
  local io_weight="$DEFAULT_IO_WEIGHT"

  case "$profile" in
    strict)
      memory_mb=256
      cpu_quota=50000
      pids_limit=50
      ;;
    permissive)
      memory_mb=1024
      cpu_quota=200000
      pids_limit=200
      ;;
  esac

  echo "$((memory_mb * 1024 * 1024))" | sudo tee "$cgroup_path/memory.max" >/dev/null || true
  echo "$cpu_quota $cpu_period" | sudo tee "$cgroup_path/cpu.max" >/dev/null || true
  echo "$pids_limit" | sudo tee "$cgroup_path/pids.max" >/dev/null || true
  echo "default $io_weight" | sudo tee "$cgroup_path/io.weight" >/dev/null || true
  echo "$pid" | sudo tee "$cgroup_path/cgroup.procs" >/dev/null || true

  echo "✅ Resource limits aplicados via cgroups v2 (PID $pid)"
}

###############################################################################
# Monitor de recursos em tempo real
###############################################################################
monitor_resources() {
  local pid="${1:?PID required}"
  local duration="${2:-30}"
  local interval="${3:-1}"

  if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq não disponível para gerar relatório JSON" >&2
    return 1
  fi

  local output_file=".buildtovalue/reports/resource-usage-$pid.jsonl"
  mkdir -p "$(dirname "$output_file")"

  echo "📊 Monitorando recursos do PID $pid por ${duration}s..."

  local elapsed=0
  while [[ $elapsed -lt $duration ]] && kill -0 "$pid" 2>/dev/null; do
    local cpu_percent mem_percent mem_rss_kb threads
    cpu_percent=$(ps -p "$pid" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
    mem_percent=$(ps -p "$pid" -o %mem= 2>/dev/null | tr -d ' ' || echo "0")
    mem_rss_kb=$(ps -p "$pid" -o rss= 2>/dev/null | tr -d ' ' || echo "0")
    threads=$(ps -p "$pid" -o nlwp= 2>/dev/null | tr -d ' ' || echo "0")

    jq -nc \
      --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
      --arg pid "$pid" \
      --arg cpu "$cpu_percent" \
      --arg mem "$mem_percent" \
      --arg rss "$mem_rss_kb" \
      --arg threads "$threads" \
      '{
        timestamp: $ts,
        pid: ($pid | tonumber),
        cpu_percent: ($cpu | tonumber),
        mem_percent: ($mem | tonumber),
        mem_rss_kb: ($rss | tonumber),
        threads: ($threads | tonumber)
      }' >>"$output_file"

    sleep "$interval"
    elapsed=$((elapsed + interval))
  done

  echo "✅ Monitoramento concluído: $output_file"
}

###############################################################################
# Gera relatório de uso de recursos
###############################################################################
generate_resource_report() {
  local usage_file="${1:?Usage file required}"

  if [[ ! -f "$usage_file" ]]; then
    echo "❌ Arquivo não encontrado: $usage_file" >&2
    return 1
  fi

  if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq não disponível" >&2
    return 1
  fi

  echo "📊 Relatório de Uso de Recursos"
  echo "================================"

  local max_cpu avg_cpu max_mem avg_mem max_threads
  max_cpu=$(jq -s 'map(.cpu_percent) | max // 0' "$usage_file")
  avg_cpu=$(jq -s 'map(.cpu_percent) | (add // 0) / (length // 1 + 1e-9)' "$usage_file")
  max_mem=$(jq -s 'map(.mem_rss_kb) | max // 0' "$usage_file")
  avg_mem=$(jq -s 'map(.mem_rss_kb) | (add // 0) / (length // 1 + 1e-9)' "$usage_file")
  max_threads=$(jq -s 'map(.threads) | max // 0' "$usage_file")

  printf 'CPU:\n  Máximo: %.2f%%\n  Médio: %.2f%%\n\n' "$max_cpu" "$avg_cpu"
  printf 'Memória:\n  Máximo: %.2f MB\n  Médio: %.2f MB\n\n' \
    "$(awk "BEGIN {printf \"%.2f\", $max_mem / 1024}")" \
    "$(awk "BEGIN {printf \"%.2f\", $avg_mem / 1024}")"
  printf 'Threads:\n  Máximo: %s\n' "$max_threads"
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    docker-limits)
      apply_docker_limits "${2:?Container name required}" "${3:-default}"
      ;;
    cgroup-limits)
      apply_cgroup_limits "${2:?PID required}" "${3:-default}"
      ;;
    monitor)
      monitor_resources "${2:?PID required}" "${3:-30}" "${4:-1}"
      ;;
    report)
      generate_resource_report "${2:?Usage file required}"
      ;;
    *)
      echo "Uso: $0 {docker-limits|cgroup-limits|monitor|report} [args]"
      exit 1
      ;;
  esac
fi
