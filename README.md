# ConciliaIA

Sistema de **reconciliação financeira** para e-commerce e varejo: concilia as
vendas do lojista com os relatórios das adquirentes (Cielo, Rede, Stone),
detecta divergências (MDR, NSU ausente, chargeback, atraso de liquidação) e
expõe tudo numa API versionada e num dashboard.

> **Arquitetura:** monólito modular, **funcional em Docker e escalável por
> design**. Uma única imagem da aplicação (frontend estático + FastAPI) com
> **PostgreSQL externo**. Ver [`docs/ARCHITECTURE-POSTURE.md`](docs/ARCHITECTURE-POSTURE.md).

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy 2 (async) · Alembic · asyncpg · APScheduler |
| Banco | PostgreSQL 15 |
| Frontend | React 18 · Vite · TypeScript · MUI (em `conciliaai-frontend/`) |
| Empacotamento | Imagem única da app (Docker) + Postgres como serviço externo |

## Quick start (Docker)

Pré-requisitos: Docker + Docker Compose.

```bash
cp .env.example .env          # ajuste SECRET_KEY (openssl rand -hex 32) e credenciais
docker compose up --build     # sobe postgres (externo) + a imagem da app
```

No startup, a imagem da aplicação executa automaticamente:

1. `alembic upgrade head` — aplica as migrations (`0001_initial`, `0002_reconciliation_jobs`);
2. `python scripts/seed_database.py` — seed **idempotente** (tenant + 100 vendas/95 transações + usuário de teste);
3. `uvicorn src.api.main:app` — sobe a API em `:8000`, **servindo também o frontend estático**.

Acesse:

- App + API: <http://localhost:8000>
- Swagger / OpenAPI: <http://localhost:8000/docs>
- Healthcheck: <http://localhost:8000/api/v1/health>

Credenciais de teste do seed: `test@example.com` / `SecurePassword123!`.

### Targets do Makefile

```
make help          # lista os targets
make docker-up     # docker compose up -d
make docker-down   # docker compose down
make docker-logs   # logs do backend
make docker-reset  # derruba e recria (apaga o volume do Postgres)
make migrate       # alembic upgrade head no container
make start         # build + up
```

## Desenvolvimento local (sem Docker)

Backend:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                       # DATABASE_URL apontando para o seu Postgres
alembic upgrade head
python scripts/seed_database.py
uvicorn src.api.main:app --reload --port 8000
```

Frontend (dev server com proxy para `:8000`):

```bash
cd conciliaai-frontend
npm install
npm run dev                                # http://localhost:3000
```

## API

Toda a API é versionada sob **`/api/v1`** (incluindo autenticação em
`/api/v1/auth/*`). Os erros seguem um envelope padronizado
`{ detail, error_code, request_id }` com header `X-Request-ID`.

Destaques:

- **Autenticação:** `POST /api/v1/auth/login` → `{access_token, refresh_token, token_type, expires_in}`.
- **Vendas / Transações:** CRUD + importação CSV/EDI + export.
- **Reconciliação assíncrona:** `POST /api/v1/reconciliation-jobs` (202) → `GET .../{id}/status` (polling) → `GET .../metrics`.
- **Divergências / Matches:** dados reais por tenant, com resolução de divergências.
- **Extensibilidade:** `GET /api/v1/acquirers` (registro plugável de parsers) e `GET /api/v1/reconciliation-rules` (tabela de decisão de auto-approval/SLA por tenant).

Referência completa em [`docs/API-REFERENCE.md`](docs/API-REFERENCE.md).

## Estrutura do projeto

```
src/
  api/              # FastAPI: main, dependencies, middleware, errors, rotas
    v1/routes/      # endpoints versionados (/api/v1/*)
    routes/         # auth, notifications, cash_flow (montados sob /api/v1)
  application/      # services, use_cases, strategies (matching)
  domain/           # entities, value_objects, repositories (interfaces)
  infrastructure/   # persistence (SQLAlchemy/Postgres), acquirers, security, scheduler
conciliaai-frontend/  # React + Vite + MUI
alembic/              # migrations (0001_initial, 0002_reconciliation_jobs)
scripts/              # seed_database, run_migrations, create-schema.sql, ...
docs/                 # documentação
```

## Testes e CI

```bash
pytest tests/unit                       # testes unitários
pytest tests/integration -m integration # testes de integração (requer Postgres)
flake8 src/ tests/                      # lint (config em setup.cfg)
```

CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em `master`/`main`/`develop`
— flake8 → mypy (advisory) → `alembic upgrade head` → `pytest tests/unit` → `pytest tests/integration`.

## Documentação

- [`docs/ARCHITECTURE-POSTURE.md`](docs/ARCHITECTURE-POSTURE.md) — postura arquitetural (Docker único, escalável por design, backlog estratégico).
- [`docs/API-REFERENCE.md`](docs/API-REFERENCE.md) — referência da API.
- [`docs/SECURITY.md`](docs/SECURITY.md) — modelo de segurança.
- [`docs/ACQUIRER_INTEGRATIONS.md`](docs/ACQUIRER_INTEGRATIONS.md) — integrações com adquirentes.
- [`docs/business/`](docs/business/) e [`docs/ux/`](docs/ux/) — domínio de negócio e UX.

## Licença

Ver [`LICENSE`](LICENSE).
