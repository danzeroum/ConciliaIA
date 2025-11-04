#!/usr/bin/env bash
# BuildToValue v7.4-Platinum Phase 2 - Sandbox Executor
# Com Resource Limits e Seccomp Profiles
set -euo pipefail

WORKDIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SECCOMP_DIR="$WORKDIR/scripts/security/seccomp-profiles"
RESOURCE_LIMITER="$WORKDIR/scripts/security/resource-limiter.sh"

###############################################################################
# Seleciona perfil de segurança baseado no contexto
###############################################################################
select_security_profile() {
  local task_desc="${1:-}"

  if [[ -z "$task_desc" ]]; then
    echo "default"
    return 0
  fi

  if echo "$task_desc" | grep -qiE "(password|secret|key|token|credential)"; then
    echo "strict"
    return 0
  fi

  if echo "$task_desc" | grep -qiE "(build|compile|install|setup)"; then
    echo "permissive"
    return 0
  fi

  echo "default"
}

###############################################################################
# Executa em sandbox Docker com limits
###############################################################################
sandbox_execute_docker() {
  local file="${1:?Arquivo de script obrigatório}"
  local profile="${2:-default}"

  local seccomp_profile="$SECCOMP_DIR/$profile.json"
  if [[ ! -f "$seccomp_profile" ]]; then
    echo "⚠️ Seccomp profile não encontrado: $seccomp_profile" >&2
    seccomp_profile="$SECCOMP_DIR/default.json"
  fi

  if [[ ! -x "$RESOURCE_LIMITER" ]]; then
    chmod +x "$RESOURCE_LIMITER" 2>/dev/null || true
  fi

  local docker_limits
  docker_limits=$(bash "$RESOURCE_LIMITER" docker-limits "btv-sandbox" "$profile") || docker_limits=""

  echo "🐳 Executando em Docker com perfil: $profile"

  local container_id
  container_id=$(docker run -d \
    --rm \
    --network none \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=100m \
    --security-opt "seccomp=$seccomp_profile" \
    --security-opt no-new-privileges=true \
    $docker_limits \
    --user 65534:65534 \
    -v "$(pwd)":/app:ro \
    -w /app \
    ubuntu:22.04 \
    timeout 30s bash "$file" 2>&1
  ) || return 1

  docker logs -f "$container_id" 2>&1 || true

  local exit_code
  exit_code=$(docker inspect "$container_id" --format='{{.State.ExitCode}}' 2>/dev/null || echo "1")

  if [[ "$exit_code" != "0" ]]; then
    return "$exit_code"
  fi

  return 0
}

###############################################################################
# Executa em sandbox nativo com cgroups
###############################################################################
sandbox_execute_native() {
  local file="${1:?Arquivo de script obrigatório}"
  local profile="${2:-default}"

  echo "🔒 Executando em sandbox nativo com perfil: $profile"

  local sandbox_root="/tmp/btv-sandbox-$$"
  mkdir -p "$sandbox_root"/{bin,lib,lib64,proc,tmp,app}

  cp -a /bin/bash "$sandbox_root/bin/" 2>/dev/null || true
  cp -a /lib/x86_64-linux-gnu/* "$sandbox_root/lib/" 2>/dev/null || true
  cp -a /lib64/* "$sandbox_root/lib64/" 2>/dev/null || true
  cp "$file" "$sandbox_root/app/script.sh"

  local exit_code=0
  (
    unshare -r -n -m --fork --pid bash -c "
      bash '$RESOURCE_LIMITER' cgroup-limits \$\$ '$profile' 2>/dev/null || true
      mount -t proc proc '$sandbox_root/proc' 2>/dev/null || true
      chroot '$sandbox_root' timeout 30s /bin/bash /app/script.sh
    "
  ) || exit_code=$?

  rm -rf "$sandbox_root"

  return "$exit_code"
}

###############################################################################
# Função principal de execução
###############################################################################
sandbox_execute() {
  local file="${1:?Arquivo de script obrigatório}"
  local task_context="${2:-}"

  if [[ ! -f "$file" ]]; then
    echo "❌ Arquivo não encontrado: $file" >&2
    return 1
  fi

  local profile
  profile=$(select_security_profile "$task_context")
  echo "🔐 Perfil de segurança selecionado: $profile"

  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    if sandbox_execute_docker "$file" "$profile"; then
      echo "✅ Execução Docker concluída com sucesso"
      return 0
    else
      echo "❌ Execução Docker falhou, tentando fallback nativo..." >&2
    fi
  else
    echo "⚠️ Docker não disponível, usando sandbox nativo..." >&2
  fi

  if sandbox_execute_native "$file" "$profile"; then
    echo "✅ Execução nativa concluída com sucesso"
    return 0
  fi

  echo "❌ Todas as tentativas de sandbox falharam" >&2
  return 1
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  sandbox_execute "$@"
fi
