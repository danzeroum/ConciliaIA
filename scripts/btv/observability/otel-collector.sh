#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - OpenTelemetry Collector Setup
set -euo pipefail

COLLECTOR_VERSION="${BTV_OTEL_COLLECTOR_VERSION:-0.89.0}"
INSTALL_DIR="${BTV_OTEL_INSTALL_DIR:-/usr/local/bin}"
CONFIG_DIR="${BTV_OTEL_CONFIG_DIR:-.buildtovalue/telemetry}"

###############################################################################
# Instala OpenTelemetry Collector
###############################################################################
install_otel_collector() {
  echo "📦 Instalando OpenTelemetry Collector v${COLLECTOR_VERSION}..."

  local os arch download_url tmp_dir
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)

  case "$arch" in
    x86_64) arch="amd64" ;;
    aarch64|arm64) arch="arm64" ;;
  esac

  download_url="https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${COLLECTOR_VERSION}/otelcol_${COLLECTOR_VERSION}_${os}_${arch}.tar.gz"

  echo "📥 Baixando de: $download_url"

  tmp_dir=$(mktemp -d)
  pushd "$tmp_dir" >/dev/null

  curl -L -o otelcol.tar.gz "$download_url"
  tar xzf otelcol.tar.gz

  sudo mv otelcol "$INSTALL_DIR/"
  sudo chmod +x "$INSTALL_DIR/otelcol"

  popd >/dev/null
  rm -rf "$tmp_dir"

  echo "✅ OpenTelemetry Collector instalado em: $INSTALL_DIR/otelcol"
}

###############################################################################
# Gera configuração do collector
###############################################################################
generate_collector_config() {
  mkdir -p "$CONFIG_DIR"

  local config_file="$CONFIG_DIR/otel-collector-config.yaml"

  cat >"$config_file" <<'YAML'
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  attributes:
    actions:
      - key: btv.collector.version
        value: v7.4-platinum
        action: insert

  memory_limiter:
    check_interval: 1s
    limit_mib: 512

exporters:
  jaeger:
    endpoint: ${BTV_JAEGER_ENDPOINT:-localhost:14250}
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889
    namespace: buildtovalue

  logging:
    verbosity: detailed

  file:
    path: ${BTV_TRACES_FILE:-.buildtovalue/telemetry/traces/traces.json}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [jaeger, logging, file]

    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, logging]

  telemetry:
    logs:
      level: info
    metrics:
      address: 0.0.0.0:8888
YAML

  echo "✅ Configuração gerada em: $config_file"
}

###############################################################################
# Inicia o collector
###############################################################################
start_collector() {
  local config_file="$CONFIG_DIR/otel-collector-config.yaml"

  if [[ ! -f "$config_file" ]]; then
    echo "❌ Configuração não encontrada. Execute: $0 generate-config" >&2
    return 1
  fi

  echo "🚀 Iniciando OpenTelemetry Collector..."

  "$INSTALL_DIR/otelcol" --config="$config_file" &
  local collector_pid=$!
  echo "$collector_pid" >"$CONFIG_DIR/collector.pid"

  echo "✅ Collector iniciado (PID: $collector_pid)"
  echo "📊 Métricas disponíveis em: http://localhost:8888/metrics"
  echo "📈 Prometheus endpoint: http://localhost:8889/metrics"
}

###############################################################################
# Para o collector
###############################################################################
stop_collector() {
  local pid_file="$CONFIG_DIR/collector.pid"

  if [[ ! -f "$pid_file" ]]; then
    echo "⚠️ Collector não está rodando" >&2
    return 0
  fi

  local pid
  pid=$(cat "$pid_file")

  if kill -0 "$pid" 2>/dev/null; then
    echo "🛑 Parando collector (PID: $pid)..."
    kill "$pid"
    rm -f "$pid_file"
    echo "✅ Collector parado"
  else
    echo "⚠️ Processo $pid não encontrado"
    rm -f "$pid_file"
  fi
}

###############################################################################
# Status do collector
###############################################################################
collector_status() {
  local pid_file="$CONFIG_DIR/collector.pid"

  if [[ ! -f "$pid_file" ]]; then
    echo "⚪ Collector: PARADO"
    return 1
  fi

  local pid
  pid=$(cat "$pid_file")

  if kill -0 "$pid" 2>/dev/null; then
    echo "🟢 Collector: RODANDO (PID: $pid)"
    if curl -sf http://localhost:8888/metrics >/dev/null 2>&1; then
      echo "  ✅ Health endpoint: OK"
    else
      echo "  ⚠️ Health endpoint: INACESSÍVEL"
    fi
    return 0
  fi

  echo "🔴 Collector: FALHA (PID $pid morto)"
  rm -f "$pid_file"
  return 1
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    install)
      install_otel_collector
      ;;
    generate-config)
      generate_collector_config
      ;;
    start)
      start_collector
      ;;
    stop)
      stop_collector
      ;;
    restart)
      stop_collector
      start_collector
      ;;
    status)
      collector_status
      ;;
    *)
      echo "Uso: $0 {install|generate-config|start|stop|restart|status}"
      exit 1
      ;;
  esac
fi
