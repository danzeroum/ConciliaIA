# ConciliaIA — Guia de Configuração

Toda a configuração é por **variáveis de ambiente** (copie `.env.example` para
`.env`). No Docker, o `docker-compose.yml` já define defaults sensatos para
desenvolvimento.

## Obrigatórias

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL do Postgres em formato **asyncpg**, ex.: `postgresql+asyncpg://user:pass@host:5432/db`. Usada pela aplicação. (O Alembic converte para `psycopg2` internamente.) |
| `SECRET_KEY` | Chave para assinar os JWT. A aplicação **não sobe sem ela**. Gere com `openssl rand -hex 32`. **Defina em produção** (o compose traz um default só para dev). |

## API / runtime

| Variável | Default | Descrição |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` ou `production`. Em produção, `CORS_ORIGINS` passa a valer. |
| `LOG_LEVEL` | `INFO` | Nível de log (structlog). |
| `PORT` | `8000` | Porta do uvicorn (no Docker é fixa em 8000). |
| `FRONTEND_DIST` | `/app/static` (na imagem) | Diretório do build estático do frontend servido pelo FastAPI. Se ausente/inexistente, a API roda sem servir o frontend. |
| `PYTHONPATH` | `/app:/app/src` (no compose) | Necessário para os imports `src.*`. |

## Banco (Postgres)

`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_DB` — usadas pelo serviço `postgres` do compose e por scripts. A
aplicação em si conecta via `DATABASE_URL`.

## Autenticação

| Variável | Default | Descrição |
|---|---|---|
| `JWT_ALGORITHM` | `HS256` | Algoritmo do JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | — | Presente no `.env.example`, mas **atualmente não está conectado** ao `JWTHandler`, que usa TTL fixo de **15 min** (access) e refresh de longa duração. Tratar como informativo até ser ligado. |

## CORS

| Variável | Default | Descrição |
|---|---|---|
| `CORS_ORIGINS` | vazio | Lista separada por vírgula de origens permitidas (usada quando `ENVIRONMENT=production`). Em dev usa-se `localhost:3000/5173`. Na imagem única (mesma origem), CORS é irrelevante para o app. |

## Rate limiting

| Variável | Default | Descrição |
|---|---|---|
| `RATE_LIMIT_REQUESTS_PER_MINUTE` / `RATE_LIMIT_PER_MINUTE` | `100` | Requisições por minuto por tenant/IP. |
| `RATE_LIMIT_MAX` / `RATE_LIMIT_WINDOW` | `100` / `900` | Presentes no `.env.example`; o limite efetivo é lido das variáveis acima. |

## Integração Cielo (opcional)

| Variável | Descrição |
|---|---|
| `CIELO_CONCILIATOR_BASE_URL` | URL base do Cielo Conciliator. |
| `CIELO_CONCILIATOR_CLIENT_ID` | Client ID. |
| `CIELO_CONCILIATOR_CLIENT_SECRET` | Client Secret. |

A aplicação **sobe sem** essas variáveis; as rotas Cielo
(`/api/v1/cielo-conciliator/*`) retornam **503** até serem configuradas.

## Variáveis legadas / não usadas

O `.env.example` ainda lista chaves de uma fase anterior que **não têm efeito**
no código atual e podem ser ignoradas/removidas:
`OPENAI_API_KEY`, `OLLAMA_BASE_URL`, `FREE_MODE_ENABLED`, `REDIS_HOST`,
`REDIS_PORT`, `CHROMADB_HOST`, `CHROMADB_PORT`, `PROMETHEUS_URL`,
`SLACK_WEBHOOK_URL`. (Não há Redis, ChromaDB, Prometheus ou integrações LLM no
runtime.)

## Exemplo mínimo de `.env` (dev)

```env
DATABASE_URL=postgresql+asyncpg://app_user:app_password@localhost:5432/conciliaai
SECRET_KEY=troque-por-openssl-rand-hex-32
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```
