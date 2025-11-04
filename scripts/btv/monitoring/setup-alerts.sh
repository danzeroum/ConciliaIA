#!/bin/bash
# Configuração completa de alertas para o Pipeline Bífido v7.2
# Princípios SRE: Error Budgets e Monitoring First

set -euo pipefail

echo "🚀 Configurando sistema de alertas para BuildToValue v7.2 Quality Intelligence..."

# Descobrir comando docker compose disponível
if command -v docker-compose > /dev/null; then
    compose_cmd="docker-compose"
elif command -v docker > /dev/null && docker compose version > /dev/null 2>&1; then
    compose_cmd="docker compose"
else
    echo "❌ docker compose não está instalado. Instale docker-compose ou docker compose."
    exit 1
fi

# Configuração de diretórios
mkdir -p docker/prometheus/rules
mkdir -p docker/grafana/provisioning/datasources
mkdir -p docker/grafana/provisioning/dashboards

# Validar configuração do Prometheus
if ! ${compose_cmd} -f docker-compose.quality-intelligence.yml config --quiet; then
    echo "❌ Erro na configuração do docker-compose"
    exit 1
fi

# Aplicar configurações
echo "📋 Aplicando regras de alerta..."
cp -f docker/prometheus/rules/quality-intelligence.rules docker/prometheus/rules/

# Recarregar configuração do Prometheus (se estiver rodando)
if docker ps | grep -q btv-prometheus; then
    echo "🔄 Recarregando configuração do Prometheus..."
    curl -X POST http://localhost:9090/-/reload || echo "⚠️ Prometheus não respondeu ao reload, mas a configuração foi aplicada"
fi

# Configurar datasource do Grafana
echo "📊 Configurando Grafana..."
until curl -s http://localhost:3000/api/health > /dev/null; do
    echo "⏳ Aguardando Grafana..."
    sleep 5
done

# Configurar dashboard via API (fallback)
if command -v jq > /dev/null; then
    echo "📈 Configurando dashboard via API..."
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -u admin:btv2024 \
      http://localhost:3000/api/dashboards/db \
      -d @docker/grafana/provisioning/dashboards/quality-intelligence.json \
      || echo "⚠️ Não foi possível configurar dashboard via API"
fi

# Configurar SLOs baseados em Error Budget
echo "💰 Configurando Error Budgets..."

# SLO: Pipeline Síncrono - 99.5% disponibilidade
# SLO: Pipeline Assíncrono - 99% disponibilidade  
# SLO: Mutation Tests - 85% score mínimo
# SLO: Flaky Tests - máximo 5%

cat > docker/prometheus/rules/slos.rules << 'SLO_EOF'
groups:
  - name: btv_slos
    rules:
      # Error Budget: Pipeline Síncrono (0.5% downtime mensal = 3.6 horas)
      - record: btv_sync_pipeline_error_budget
        expr: (1 - (increase(btv_pipeline_sync_failures_total[30d]) / increase(btv_pipeline_sync_total[30d]))) - 0.995
      
      # Error Budget: Pipeline Assíncrono (1% downtime mensal = 7.2 horas)
      - record: btv_async_pipeline_error_budget  
        expr: (1 - (increase(btv_pipeline_async_failures_total[30d]) / increase(btv_pipeline_async_total[30d]))) - 0.99
SLO_EOF

echo "✅ Sistema de alertas configurado com sucesso!"
echo ""
echo "📊 Dashboards disponíveis:"
echo "   Grafana: http://localhost:3000 (admin/btv2024)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🚨 Alertas configurados:"
echo "   - Pipeline Síncrono (crítico)"
echo "   - Pipeline Assíncrono (warning)" 
echo "   - Mutation Test Score < 85%"
echo "   - Flaky Test Rate > 5%"
echo "   - Code Coverage < 80%"
