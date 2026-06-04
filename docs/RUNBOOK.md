# ConciliaIA — Runbook de Operações

Operação do deploy real: **uma imagem da aplicação** (frontend + FastAPI) +
**PostgreSQL externo**, orquestrados por `docker-compose`. Não há Kubernetes,
Prometheus/Grafana nem service mesh (ver [`ARCHITECTURE-POSTURE.md`](ARCHITECTURE-POSTURE.md)).

## Subir / derrubar

```bash
docker compose up -d --build     # ou: make start
docker compose ps                # estado dos serviços (postgres, backend)
docker compose down              # derruba (mantém o volume do Postgres)
docker compose down -v           # derruba e APAGA os dados (make docker-reset)
```

No startup, o container da app executa automaticamente:
`alembic upgrade head` → `python scripts/seed_database.py` (idempotente) →
`uvicorn`. Falha de migration **aborta** o boot (sem mascaramento).

## Health & smoke

```bash
curl -fsS http://localhost:8000/api/v1/health           # 200 = ok
# login de fumaça (usuário do seed)
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"SecurePassword123!"}'
```

O `Dockerfile` define um `HEALTHCHECK` em `/api/v1/health`.

## Logs

```bash
docker compose logs -f backend     # ou: make docker-logs
docker compose logs -f postgres
```

Logs são estruturados (structlog). Toda resposta carrega `X-Request-ID`; erros
trazem `{detail, error_code, request_id}` — use o `request_id` para correlação.

## Banco de dados

```bash
# migrations
docker compose exec backend alembic upgrade head        # ou: make migrate
docker compose exec backend alembic current
docker compose exec backend alembic downgrade -1        # rollback de 1 revisão

# acesso psql
docker compose exec postgres psql -U app_user -d conciliaai

# seed manual (idempotente)
docker compose exec backend python scripts/seed_database.py
```

**Backup / restore** (Postgres é externo ao container da app — backup é do
serviço/volume do banco):

```bash
docker compose exec postgres pg_dump -U app_user conciliaai > backup.sql
cat backup.sql | docker compose exec -T postgres psql -U app_user -d conciliaai
```

## Reconciliação assíncrona

```bash
# dispara um job (202 + job_id) e acompanha o status
curl -X POST http://localhost:8000/api/v1/reconciliation-jobs \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"start_date":"2024-01-01","end_date":"2024-01-31"}'
curl http://localhost:8000/api/v1/reconciliation-jobs/$JOB_ID/status -H "Authorization: Bearer $TOKEN"
# métricas de processo (p50/p95, backlog, auto-approval)
curl http://localhost:8000/api/v1/reconciliation-jobs/metrics -H "Authorization: Bearer $TOKEN"
```

O worker é **in-process** (asyncio): jobs não sobrevivem a um restart do container
no estado `running`. Para volume maior, ver o backlog de orquestração em
`ARCHITECTURE-POSTURE.md`.

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Container da app não sobe; erro de `SECRET_KEY` | `SECRET_KEY` ausente | Definir `SECRET_KEY` no `.env`. |
| Boot aborta em "Applying Alembic migrations" | banco indisponível/credenciais | Conferir `postgres` saudável (`docker compose ps`) e `DATABASE_URL`. |
| `401` em chamadas `/api/v1/*` | token ausente/expirado | Refazer login / refresh (`/api/v1/auth/refresh`). |
| `403 Tenant not authorized` | token sem tenant válido | Reautenticar; verificar o tenant do usuário. |
| `429` | rate limit (100/min) | Reduzir taxa ou ajustar `RATE_LIMIT_REQUESTS_PER_MINUTE`. |
| Rotas Cielo retornam `503` | credenciais Cielo não configuradas | Definir `CIELO_CONCILIATOR_*` (opcional). |
| Frontend não aparece em `/` | build do frontend ausente na imagem | Conferir `FRONTEND_DIST` e o estágio de build do `Dockerfile`. |

## Configuração

Variáveis de ambiente em [`CONFIGURATION-GUIDE.md`](CONFIGURATION-GUIDE.md).
