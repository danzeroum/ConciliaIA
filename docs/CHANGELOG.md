# Changelog

Todas as mudanças notáveis do ConciliaIA. Formato baseado em
[Keep a Changelog](https://keepachangelog.com/); versionamento semântico.

## [Unreleased]

### Mudado — "funcional em Docker, escalável por design"
- **Docker único:** uma imagem da aplicação (frontend estático build + FastAPI
  servindo o estático) com **PostgreSQL externo** no `docker-compose`. Boot
  aplica `alembic upgrade head` + seed idempotente + uvicorn.
- **API versionada:** toda a superfície sob `/api/v1`, **incluindo autenticação**
  (`/api/v1/auth/*`); health em `/api/v1/health`. Removido `/auth` e `/health` antigos.
- **Envelope de erro** padronizado `{detail, error_code, request_id}` + header
  `X-Request-ID`.
- `PUT`→`PATCH` na atualização de venda; valores monetários tipados como `Decimal`
  (serializados como número JSON), sem `ALTER TABLE`.

### Adicionado
- **Reconciliação assíncrona:** tabela `reconciliation_jobs` + worker leve
  (asyncio): `POST /api/v1/reconciliation-jobs` (202) → status (polling) →
  `/metrics` (p50/p95, throughput, backlog, taxa de auto-approval).
- **Extensibilidade:** `GET /api/v1/acquirers` (registro plugável de parsers) e
  `GET /api/v1/reconciliation-rules` (tabela de decisão de auto-approval/SLA por
  tenant, via `tenant.features`).
- Migrations Alembic `0001_initial` e `0002_reconciliation_jobs`; seed idempotente
  com usuário de teste.

### Corrigido
- Bloqueador de auth: o contexto do JWT passou a ser populado por
  `JWTContextMiddleware` (antes `request.state.tenant_id` ficava vazio → 403 em
  toda chamada). Sem token → **401**.
- Divergences/Matches passam a retornar **dados reais** do banco (fim dos
  `div-001`/`match-001`).
- `AcquirerTransaction` normaliza `datetime`→`date`; estratégias de match geram
  UUID válido; parsers OFX/Cielo Agiliza/Rede EDI corrigidos.

### Removido
- Todo o scaffolding "BuildToValue" (framework de orquestração de IA), a stack de
  monitoramento (Prometheus/Grafana/ChromaDB), IaC/Terraform, a stack paralela
  Node/TypeScript + Prisma e os workflows de governança. O repositório passou a
  ser apenas o produto ConciliaIA + Docker.

### CI
- Workflow único `.github/workflows/ci.yml`: flake8 (`setup.cfg`) → mypy
  (advisory) → `alembic upgrade head` → `pytest tests/unit` → `pytest tests/integration`.

---

## [7.0.0] — 2025-10-19 — Initial release

### Adicionado
- **Domínio:** value objects (`Money`, `NSU`, `Percentage`, …), entidades
  (`Sale`, `AcquirerTransaction`, `ReconciliationMatch`, `Divergence`, …) com
  invariantes de negócio e type hints.
- **Engine de matching:** `ExactMatcher`, `FuzzyMatcher`, `InstallmentMatcher`,
  `MLMatcher` em cascata, com auto-aprovação por confiança.
- **Detecção de anomalias:** 6 tipos de divergência com severidade e ação sugerida.
- **Use case** `ReconcileTransactionsUseCase` com cálculo de métricas.
- **PostgreSQL (async SQLAlchemy):** repositórios, índices, isolamento por tenant.
- **Adquirentes:** parsers Cielo/Rede (EDI) e cliente Stone.
- **Auth & RBAC:** JWT (access + refresh), bcrypt (12 rounds), rate limiting
  (100 req/min), middleware multi-tenant.
- **Testes:** unit + integration + e2e.

### Segurança (implementada)
- JWT (HS256), hash de senha bcrypt 12 rounds, rate limiting (token bucket),
  isolamento multi-tenant na aplicação, proteção contra SQL injection via ORM,
  cabeçalhos `X-Content-Type-Options`/`X-Frame-Options`/HSTS.

> Correções de histórico: notas anteriores citavam Kubernetes, Prometheus/Grafana,
> ELK, RLS no Postgres, gate de cobertura de 87% e testes Locust/K6 — nada disso
> existe no código. Ver [`SECURITY.md`](SECURITY.md) e
> [`ARCHITECTURE-POSTURE.md`](ARCHITECTURE-POSTURE.md) para o estado real.

## Histórico de versões

- v7.0.0 (2025-10-19) — primeira release
- v0.2.0-beta (2025-09-01) — beta com clientes piloto
- v0.1.0-alpha (2025-01-15) — testes internos
