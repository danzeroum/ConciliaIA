#!/bin/bash
# PATCH-C: Contratos da Operator-GUI
set -euo pipefail

echo "🔧 PATCH-C: Contratos da BTV-Operator-GUI"
echo "=========================================="

# PATCH-C1: Criar estrutura de specs
echo "1️⃣ Criando estrutura de especificações..."
mkdir -p specs/operator-gui contracts/operator-gui

# OpenAPI stub
cat > specs/operator-gui/openapi.yaml <<'OPENAPI'
openapi: 3.1.0
info:
  title: BTV Operator GUI API
  version: 0.1.0
  description: API interna da GUI Operacional do BuildToValue v7.1
  contact:
    name: BuildToValue Squad
    email: squad@buildtovalue.dev

servers:
  - url: http://localhost:8080/api/v1
    description: Desenvolvimento local

paths:
  /metrics/what-matters:
    get:
      operationId: getWhatMatters
      summary: Retorna métricas agregadas para o painel principal
      tags:
        - Metrics
      responses:
        '200':
          description: Métricas carregadas com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WhatMatters'
        '404':
          description: Arquivo de métricas não encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /ledger/recent-decisions:
    get:
      operationId: getRecentDecisions
      summary: Lista decisões recentes do ledger
      tags:
        - Ledger
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: Lista de decisões
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Decision'

  /architecture/ownership-map:
    get:
      operationId: getOwnershipMap
      summary: Retorna o mapa de ownership de serviços
      tags:
        - Architecture
      responses:
        '200':
          description: Ownership map
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OwnershipMap'

components:
  schemas:
    WhatMatters:
      type: object
      required:
        - generated_at
        - window_days
      properties:
        generated_at:
          type: string
          format: date-time
        window_days:
          type: integer
        dora_metrics:
          type: object
          properties:
            deployment_frequency:
              type: number
            lead_time_hours:
              type: number
            mttr_hours:
              type: number
            change_failure_rate:
              type: number
        quality_metrics:
          type: object
          properties:
            test_coverage:
              type: number
            code_complexity:
              type: number
            security_issues:
              type: integer

    Decision:
      type: object
      required:
        - id
        - timestamp
        - agent
        - task
        - outcome
      properties:
        id:
          type: string
        timestamp:
          type: string
          format: date-time
        agent:
          type: string
        task:
          type: string
        outcome:
          type: string
          enum: [success, failure, partial]
        confidence:
          type: number
          minimum: 0
          maximum: 1

    OwnershipMap:
      type: object
      additionalProperties:
        type: object
        properties:
          owner:
            type: string
          slo_target:
            type: number
          dependencies:
            type: array
            items:
              type: string

    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
        message:
          type: string
OPENAPI

echo "   ✅ OpenAPI spec criado: specs/operator-gui/openapi.yaml"

# Contrato de telemetria
cat > contracts/operator-gui/telemetry.json <<'TELE'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BTV Operator GUI Telemetry Contract",
  "version": "1.0.0",
  "source_files": [
    ".buildtovalue/reports/what-matters.json",
    "docs/architecture/ownership-map.md"
  ],
  "refresh_policy": "on-change",
  "data_sources": {
    "ledger": {
      "type": "postgresql",
      "connection": "postgres://btv_user@localhost:5432/buildtovalue",
      "tables": ["ledger_decisions", "ledger_prompts"]
    },
    "metrics": {
      "type": "file",
      "path": ".buildtovalue/reports/what-matters.json",
      "format": "json",
      "fallback": {
        "generated_at": "",
        "window_days": 7,
        "dora_metrics": {},
        "quality_metrics": {}
      }
    },
    "ownership": {
      "type": "file",
      "path": "docs/architecture/ownership-map.md",
      "format": "markdown",
      "fallback": "# Ownership Map\n\n_Ainda não gerado_"
    }
  },
  "update_frequency": {
    "ledger": "real-time",
    "metrics": "hourly",
    "ownership": "on-demand"
  }
}
TELE

echo "   ✅ Contrato de telemetria criado: contracts/operator-gui/telemetry.json"

# PATCH-C2: Garantir que what-matters.json existe
echo "2️⃣ Garantindo existência de what-matters.json..."
mkdir -p .buildtovalue/reports

cat > .buildtovalue/reports/what-matters.json <<'MATTERS'
{
  "generated_at": "",
  "window_days": 7,
  "dora_metrics": {
    "deployment_frequency": 0,
    "lead_time_hours": 0,
    "mttr_hours": 0,
    "change_failure_rate": 0
  },
  "quality_metrics": {
    "test_coverage": 0,
    "code_complexity": 0,
    "security_issues": 0
  },
  "_note": "Este é um arquivo placeholder. Será populado por scripts de métricas."
}
MATTERS

echo "   ✅ what-matters.json criado com valores placeholder"

# PATCH-C3: Criar ownership-map.md stub
echo "3️⃣ Criando ownership-map.md stub..."
mkdir -p docs/architecture

cat > docs/architecture/ownership-map.md <<'OWN'
# 🗺️ BuildToValue v7.1 - Service Ownership Map

## Última Atualização
_Ainda não gerado automaticamente_

## Serviços Mapeados

### orchestrator
- **Owner**: ia-arquiteto
- **SLO Target**: 99.5%
- **Dependencies**: postgres, redis, chromadb

### ledger
- **Owner**: ia-qa
- **SLO Target**: 99.9%
- **Dependencies**: postgres

### validation
- **Owner**: ia-qa
- **SLO Target**: 99.0%
- **Dependencies**: none

---

💡 **Como atualizar**: Execute `./scripts/architecture/generate-ownership-map.sh`
OWN

echo "   ✅ ownership-map.md stub criado"

echo ""
echo "✅ PATCH-C concluído: Contratos da GUI prontos"
