#!/usr/bin/env bash
set -euo pipefail

ROOT="${BASH_SOURCE[0]%/*}/../.."
CATALOG="$ROOT/docs/architecture/sla-catalog.yaml"
OUT="$ROOT/docs/architecture/ownership-map.md"
TRACING_DATA="$ROOT/.buildtovalue/reports/tracing-summary.json"
TIMESTAMP=$(date -Iseconds)

# Validar dependências
command -v yq >/dev/null 2>&1 || {
  echo "❌ yq não encontrado. Instale no ambiente:"
  echo "   • Ubuntu/Debian: apt-get install yq"
  echo "   • macOS: brew install yq"
  echo "   • Manual: https://github.com/mikefarah/yq/releases"
  echo ""
  echo "   CI/CD já instala automaticamente via workflow."
  exit 1
}

command -v jq >/dev/null 2>&1 || {
  echo "❌ jq não encontrado. Instale: apt-get install jq (ou brew install jq)"
  exit 1
}

# Validar catálogo existe
[ ! -f "$CATALOG" ] && {
  echo "⚠️  Catálogo SLA não encontrado. Criando template..."
  mkdir -p "$(dirname "$CATALOG")"
  cat > "$CATALOG" <<'YAML'
version: 1
last_updated: $(date -Iseconds)
services:
  - name: example-service
    owner: SQUAD-Core
    oncall: "@oncall-core"
    slos:
      availability: 
        target: 99.5
        window: "30d"
      latency_p95_ms: 
        target: 300
        window: "30d"
    dependencies: ["db-main", "auth-svc"]
    telemetry:
      health: "/healthz"
      metrics: "/metrics"
      tracing_endpoint: "jaeger.internal:4317"
YAML
  echo "✅ Template criado em $CATALOG"
}

# Integração com tracing real (se disponível)
TRACING_DEPS=""
if [ -f "$TRACING_DATA" ]; then
  TRACING_DEPS=$(jq -r '.services[] | "\(.name):\(.dependencies | join(","))"' "$TRACING_DATA" 2>/dev/null || true)
fi

# Gerar header com metadata
cat > "$OUT" <<HEADER
# Ownership Map (Vivo)

**Gerado em:** $TIMESTAMP  
**Fonte:** `sla-catalog.yaml` + OpenTelemetry traces  
**Comando:** `./scripts/architecture/generate-ownership-map.sh`

> 📊 **Error Budget** é calculado automaticamente: `(1 - SLO) × window × 60`  
> 🔄 **Dependências** são enriquecidas com dados de tracing quando disponíveis

---

| Serviço/Componente | Owner (Squad) | On-call | Dependências | SLO Alvo | Error Budget (min) | Observabilidade |
|---|---|---|---|---|---|---|
HEADER

# Parser robusto usando yq (suporta arrays e objetos complexos)
yq eval '.services[]' "$CATALOG" | yq eval -o=json '.' | jq -r '
  .name as $svc |
  .owner as $own |
  .oncall as $onc |
  (.dependencies // [] | join(", ")) as $deps |
  (.slos.availability.target // 0) as $avail |
  (.slos.availability.window // "30d") as $window |
  (.telemetry.health // "-") as $health |
  (.telemetry.metrics // "-") as $metrics |
  
  # Calcular error budget: (1 - SLO/100) * dias * 1440 min/dia
  (if $window == "30d" then 43200 else 0 end) as $window_min |
  (($window_min * (1 - $avail / 100)) | floor) as $error_budget |
  
  "| \($svc) | \($own) | \($onc) | \($deps) | \($avail)% \($window) | \($error_budget) | \($health), \($metrics) |"
' >> "$OUT"

# Enriquecer com dados de tracing (se disponível)
if [ -n "$TRACING_DEPS" ]; then
  echo -e "\n---\n\n## 🔍 Dependências Detectadas por Tracing\n" >> "$OUT"
  echo "$TRACING_DEPS" | while IFS=: read -r svc deps; do
    echo "- **$svc** → \`$deps\`" >> "$OUT"
  done
fi

# Adicionar footer com instruções
cat >> "$OUT" <<FOOTER

---

## 📝 Como Atualizar

1. **Editar catálogo:** `$CATALOG`
2. **Regenerar mapa:** `./scripts/architecture/generate-ownership-map.sh`
3. **Versionar:** `git add docs/architecture/ && git commit -m "docs: update ownership map"`

## 🔗 Integrações

- **Tracing:** OpenTelemetry → `.buildtovalue/reports/tracing-summary.json`
- **Métricas:** Prometheus → `/monitoring/dashboards/ownership.json`

## 📊 Calcular Error Budget Atual

```
bash
# Exemplo: serviço com 99.5% SLO em 30 dias = 216 min de downtime permitido
# Se já usou 50 min, restam 166 min (76.9% do budget)
./scripts/monitoring/calculate-error-budget.sh --service=example-service
```
FOOTER

# Validar schema do catálogo (se schema JSON disponível)
if [ -f "$ROOT/.buildtovalue/schemas/sla-catalog.schema.json" ]; then
  yq eval -o=json "$CATALOG" > /tmp/catalog.$$.json
  ajv validate -s "$ROOT/.buildtovalue/schemas/sla-catalog.schema.json" -d /tmp/catalog.$$.json 2>&1 || {
    echo "⚠️  Catálogo possui erros de schema. Mapa pode estar incompleto."
  }
  rm -f /tmp/catalog.$$.json
fi

# Registrar no ledger
if [ -f "$ROOT/scripts/ledger/auto-log-decision.sh" ]; then
  "$ROOT/scripts/ledger/auto-log-decision.sh" \
    "ia-arquiteto" \
    "Regeneração do ownership map com $(yq eval '.services | length' "$CATALOG") serviços" \
    "success" \
    0.95
fi

echo "✅ Ownership map gerado em $OUT"
echo "📊 $(yq eval '.services | length' "$CATALOG") serviços documentados"
