# ConciliaIA — API Reference

API de reconciliação financeira. Toda a superfície é versionada sob **`/api/v1`**.
Base URL em desenvolvimento: `http://localhost:8000`. Na imagem única, o frontend
e a API compartilham a mesma origem (chamadas relativas).

OpenAPI interativo: **`/docs`** (Swagger) e **`/redoc`**. Schema: **`/openapi.json`**.

## Autenticação

JWT (HS256). Faça login e envie o token no header `Authorization: Bearer <access_token>`.

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/auth/login` | Login. Body `{email, password}` → `{access_token, refresh_token, token_type:"bearer", expires_in}` |
| POST | `/api/v1/auth/refresh` | Renova o token. Body `{refresh_token}` |
| POST | `/api/v1/auth/logout` | Logout |

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePassword123!"}'
```

Endpoints sob `/api/v1` (exceto `/api/v1/health` e `/api/v1/auth/*`) exigem token
válido — sem ele, a resposta é **401** (permite o refresh automático no frontend).

## Envelope de erro

Todas as respostas de erro seguem o formato abaixo, e toda resposta carrega o
header `X-Request-ID`:

```json
{ "detail": "Sale not found", "error_code": "not_found", "request_id": "f1c2…" }
```

`error_code` mapeia o status (`bad_request`, `unauthorized`, `forbidden`,
`not_found`, `validation_error`, `rate_limit_exceeded`, `internal_error`, …).

## Health

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/health` | Healthcheck (público) |

## Vendas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/sales` | Lista paginada (filtros: `start_date`, `end_date`, `payment_method`, `matched`, `nsu`, `page`, `page_size`) |
| POST | `/api/v1/sales` | Cria venda (201) |
| GET | `/api/v1/sales/{sale_id}` | Detalhe |
| PATCH | `/api/v1/sales/{sale_id}` | Atualização parcial |
| DELETE | `/api/v1/sales/{sale_id}` | Remove (204) |
| POST | `/api/v1/sales/import` | Importa CSV (multipart) |
| GET | `/api/v1/sales/export/csv` | Exporta CSV |

Valores monetários trafegam como número JSON (tipados como `Decimal` no backend;
colunas `Numeric(15,2)`).

## Transações (adquirentes)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/transactions` | Lista |
| GET | `/api/v1/transactions/{transaction_id}` | Detalhe |
| POST | `/api/v1/transactions/import` | Importa CSV |
| POST | `/api/v1/transactions/import-edi` | Importa EDI (`acquirer` query, default `rede`) |
| GET | `/api/v1/transactions/export/csv` | Exporta CSV |

## Reconciliação

### Síncrona

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/reconciliation/execute` | Executa reconciliação para um período (`start_date`, `end_date`) |

### Assíncrona (recomendada)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/reconciliation-jobs` | Dispara job → **202** `{job_id, status}` |
| GET | `/api/v1/reconciliation-jobs` | Lista jobs recentes |
| GET | `/api/v1/reconciliation-jobs/{job_id}/status` | Status do job (polling) |
| GET | `/api/v1/reconciliation-jobs/metrics` | Métricas de processo (p50/p95 de duração, throughput de matches, backlog de divergências, taxa de auto-approval) |

### Regras de decisão (auto-approval / SLA)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/reconciliation-rules` | Tabela de decisão efetiva do tenant (limiar de auto-approval e SLAs por severidade). Override por tenant em `tenant.features['reconciliation_policy']` |

## Divergências e Matches

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/divergences` | Lista paginada (filtros: `status`, `type`, `severity`, `page`, `page_size`) |
| GET | `/api/v1/divergences/{divergence_id}` | Detalhe |
| PATCH | `/api/v1/divergences/{divergence_id}/resolve` | Resolve divergência |
| GET | `/api/v1/matches` | Matches recentes (`limit`) |

## Adquirentes

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/acquirers` | Lista adquirentes e formatos de parser disponíveis (registro plugável) |

Ver [`ACQUIRER_INTEGRATIONS.md`](ACQUIRER_INTEGRATIONS.md).

## Relatórios e Estatísticas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/stats/dashboard` | KPIs do dashboard |
| GET | `/api/v1/stats/kpis` | KPIs |
| GET | `/api/v1/reports/accuracy` | Acurácia |
| GET | `/api/v1/reports/acquirer-performance` | Desempenho por adquirente |
| GET | `/api/v1/reports/cashflow-overview` | Visão de fluxo de caixa |
| GET | `/api/v1/reports/divergence-analysis` | Análise de divergências |
| GET | `/api/v1/reports/mdr-variance` | Variância de MDR |
| GET | `/api/v1/reports/settlement-analysis` | Análise de liquidação |
| GET | `/api/v1/export/sales/excel` | Export Excel de vendas |
| GET | `/api/v1/export/reports/accuracy/excel` | Export Excel de acurácia |
| GET | `/api/v1/export/reports/divergences/excel` | Export Excel de divergências |

## Conciliação bancária (OFX)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/bank-reconciliation/upload-ofx` | Upload de extrato OFX |
| POST | `/api/v1/bank-reconciliation/auto-match` | Conciliação automática |

## Outros

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/cash-flow/forecast` | Previsão de fluxo de caixa |
| GET/POST/PUT/DELETE | `/api/v1/auto-import/schedule[/{id}]` | Agendamentos de import automático |
| POST | `/api/v1/cielo-conciliator/import` | Import via Cielo Conciliator (requer credenciais Cielo; 503 se não configurado) |
| POST | `/api/v1/ingestion/rede-torc` | Ingestão Rede TORC |
| GET | `/api/v1/alerts/proactive` | Alertas proativos |
| GET | `/api/v1/notifications/` | Notificações |
| GET | `/api/v1/notifications/unread-count` | Contagem de não lidas |
| POST | `/api/v1/notifications/{id}/mark-read` | Marca como lida |

---

> Esta referência é mantida à mão; a fonte da verdade é o OpenAPI gerado em
> tempo de execução (`/openapi.json`).
