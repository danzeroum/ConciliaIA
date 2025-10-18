# ⚙️ BuildToValue v7.0 – Configuration Guide

Step-by-step handbook for configuring BuildToValue across development, staging, and production environments. Pair this guide with `.env.example` and the scripts in `./scripts/config/`.

---

## 📑 Table of Contents

1. [Configuration Philosophy](#configuration-philosophy)
2. [Configuration Files Overview](#configuration-files-overview)
3. [Environment Variable Reference](#environment-variable-reference)
    - [Core Application](#core-application)
    - [Database](#database)
    - [Cache](#cache)
    - [Vector Database (Auto-RAG)](#vector-database-auto-rag)
    - [Orchestration](#orchestration)
    - [Squad & Personas](#squad--personas)
    - [Learning System](#learning-system)
    - [Observability](#observability)
    - [Security](#security)
    - [Integrations](#integrations)
    - [Docker](#docker)
    - [Feature Flags](#feature-flags)
4. [Environment Profiles](#environment-profiles)
5. [Validation Workflow](#validation-workflow)
6. [Secrets Management](#secrets-management)
7. [Troubleshooting Configuration](#troubleshooting-configuration)
8. [Appendix: Example Templates](#appendix-example-templates)

---

## Configuration Philosophy

- **Explicit over implicit:** every feature should be toggled via environment variables or YAML config.
- **Immutable infrastructure:** treat `.env.*` files as generated artifacts; edit via scripts when possible.
- **Separation of concerns:** keep credentials in secrets managers, store non-sensitive defaults in git.
- **Environment parity:** align dev/staging/prod values to avoid surprises (feature flags should toggle behaviour, not hide missing configuration).

---

## Configuration Files Overview

| File | Purpose | Notes |
|------|---------|-------|
| `.env.example` | Baseline template with documentation | Copy to `.env.dev`, `.env.staging`, `.env.prod` |
| `.buildtovalue/config/quality-gates.yaml` | Thresholds for gates | Align with foundation level |
| `.buildtovalue/orchestration/activation-matrix.yaml` | Routing triggers | Keep domain-specific patterns here |
| `.buildtovalue/orchestration/decision-rights.yaml` | Conflict resolution policy | Review quarterly |
| `.buildtovalue/squad/personas/*.yaml` | Persona definitions | Use `validate-personas.sh` after edits |
| `docker-compose.yml` | Local runtime services | Mirror env vars via `${VAR}` syntax |
| `docker-compose-prod.yml` | Production stack | Includes replicas, scaling, security hardening |

---

## Environment Variable Reference

### Core Application

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `PROJECT_NAME` | Display name in dashboards and ADRs | `my-awesome-project` | Keep short, slug friendly |
| `PROJECT_DESCRIPTION` | Short summary for onboarding | `"Brief description of your project"` | Appears in onboarding scripts |
| `PROJECT_DOMAIN` | Domain specialisation | `saas` | Options: fintech, healthtech, saas, ecommerce, gaming, other |
| `FOUNDATION_LEVEL` | Feature bundle | `standard` | `lite`, `standard`, `enterprise` |
| `ENVIRONMENT` | Deployment environment | `development` | Influences logging verbosity |
| `DEBUG` | Enable debug logging | `true` | Disable in production |
| `OPENAI_API_KEY` | Primary LLM provider key | `sk-your-openai-key-here` | Required for assisted/autonomous modes |
| `OPENAI_MODEL` | Default OpenAI model | `gpt-4` | Consider `gpt-4-turbo` for lower latency |
| `OLLAMA_ENABLED` | Toggle local LLM fallback | `false` | Set `OLLAMA_BASE_URL` when true |

### Database

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `POSTGRES_HOST` | Hostname | `localhost` | Use `postgres` inside Docker network |
| `POSTGRES_PORT` | Port | `5432` | Keep open in firewall rules |
| `POSTGRES_DB` | Database name | `buildtovalue` | Use separate DB for tests |
| `POSTGRES_USER` | Username | `btv_user` | Rotate for production |
| `POSTGRES_PASSWORD` | Password | `change_me_in_production` | Store in secrets manager |
| `POSTGRES_POOL_MIN/MAX` | Connection pool | `2` / `10` | Tune for workload |
| `POSTGRES_BACKUP_*` | Backup toggle/schedule | `true` / `0 2 * * *` | Use offsite storage for prod |

### Cache

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `REDIS_HOST` | Hostname | `localhost` | Use `redis` inside Docker network |
| `REDIS_PORT` | Port | `6379` | Secure via ACL in production |
| `REDIS_PASSWORD` | Password | _empty_ | Set strong password in prod |
| `REDIS_KEY_PREFIX` | Namespacing | `btv:` | Avoid collisions |
| `REDIS_TTL` | Default TTL (seconds) | `3600` | Lower for bursty workloads |

### Vector Database (Auto-RAG)

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `CHROMADB_HOST` | Hostname | `localhost` | Use `chromadb` in Docker |
| `CHROMADB_PORT` | Port | `8000` | Ensure firewall open |
| `CHROMADB_COLLECTION` | Default collection | `decisions` | Separate for tests |
| `EMBEDDINGS_MODEL` | Sentence transformer | `all-MiniLM-L6-v2` | Align with RAG accuracy needs |
| `RAG_ENABLED` | Enable Auto-RAG | `true` | Set false if offline |
| `RAG_SIMILARITY_THRESHOLD` | Minimum similarity | `0.85` | Lower values return more results |

### Orchestration

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `ORCHESTRATION_MODE` | manual/assisted/autonomous | `assisted` | Use `manual` when onboarding |
| `ROUTING_CONFIDENCE_THRESHOLD` | Minimum confidence | `0.75` | Increase for critical workloads |
| `ROUTING_USE_ML` | ML-based routing | `true` | Requires historical data |
| `ROUTING_USE_RAG` | Historical context | `true` | Depends on ChromaDB |
| `ROUTING_CACHE_ENABLED` | Cache recommendations | `true` | Uses Redis |
| `COST_TRACKING_ENABLED` | Enable token spend tracking | `true` | Powers FinOps dashboards |
| `COST_DAILY_LIMIT` | Daily spend cap (USD) | `10.00` | Set 0 for unlimited |
| `COST_ALERT_THRESHOLD` | Alert when hitting % of limit | `0.80` | Notifies via Slack if enabled |

### Squad & Personas

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `DEFAULT_AUTONOMY_LEVEL` | Initial autonomy (1-5) | `3` | 1=assist only, 5=full autonomy |
| `AUTO_ADJUST_AUTONOMY` | Enable dynamic tuning | `true` | Requires ledger feedback |
| `AUTONOMY_ADJUSTMENT_THRESHOLD` | Decisions before adjustment | `10` | Higher = more stability |
| `IA_COMMUNICATION_ENABLED` | Enable inter-IA chat | `true` | Uses Redis pub/sub |
| `HANDOFF_TIMEOUT` | Seconds before escalation | `900` | Align with SLA |
| `HANDOFF_VALIDATION_STRICT` | Enforce CIIF completeness | `true` | Set false for sandbox |

### Learning System

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `RAG_MAX_RESULTS` | Max retrieval size | `5` | Increase for deep dives |
| `RAG_REINDEX_SCHEDULE` | Cron for reindexing | `0 3 * * *` | Use timezone aware cron |
| `LESSONS_LEARNED_AUTO_CAPTURE` | Auto-capture decisions | `true` | Works with ledger hooks |
| `AB_TESTING_ENABLED` | Enable experiment framework | `false` | Enterprise only |
### Observability

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `ENABLE_METRICS` | Prometheus exporter | `true` | Disable to reduce overhead |
| `ENABLE_TRACING` | OpenTelemetry tracing | `true` | Requires Jaeger/OTLP target |
| `PROMETHEUS_PORT` | Metrics port | `9090` | Expose via docker-compose |
| `LOG_LEVEL` | `debug`, `info`, `warn`, `error` | `info` | Increase to `debug` when diagnosing |
| `LOG_FORMAT` | `json` or `text` | `json` | JSON recommended for ingestion |
| `LOG_FILE_PATH` | File sink | `./logs/buildtovalue.log` | Ensure directory exists |
| `GRAFANA_ADMIN_PASSWORD` | Default `admin` | `admin` | Must change in production |

### Security

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `API_RATE_LIMIT_ENABLED` | Enable throttle | `true` | Tune for traffic |
| `API_RATE_LIMIT_REQUESTS` | Requests/min | `100` | Lower for shared environments |
| `AUTH_ENABLED` | Require auth | `false` | Enable for staging/prod |
| `AUTH_JWT_SECRET` | JWT signing key | `change-this-secret-in-production` | Rotate regularly |
| `ENCRYPTION_ENABLED` | Encrypt sensitive data | `true` | Requires `ENCRYPTION_KEY` |
| `ENCRYPTION_KEY` | Key material | _empty_ | Generate 32-byte base64 |
| `SECURITY_SCAN_ENABLED` | Daily scans | `true` | Uses `./scripts/gates/security-scan.sh` |

### Integrations

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `GIT_INTEGRATION_ENABLED` | Push ADRs to git remote | `true` | Requires `GIT_REMOTE_URL` |
| `SLACK_ENABLED` | Slack notifications | `false` | Provide webhook & channel |
| `JIRA_ENABLED` | Create tickets automatically | `false` | Provide URL, user, API token |
| `GITHUB_ENABLED` | Sync issues | `false` | Provide PAT & repo |

### Docker

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `POSTGRES_CONTAINER_NAME` | Container name | `buildtovalue-postgres` | Use in scripts |
| `DOCKER_NETWORK_NAME` | Network | `buildtovalue-network` | Ensure unique per project |
| `POSTGRES_VOLUME` | Volume | `buildtovalue-postgres-data` | Map to persistent storage |

### Feature Flags

| Variable | Description | Dev Default | Notes |
|----------|-------------|-------------|-------|
| `FEATURE_AUTO_RAG` | Auto-RAG on/off | `true` | Depends on ChromaDB |
| `FEATURE_ML_ROUTING` | ML router | `true` | Requires training data |
| `FEATURE_INTER_IA_COMM` | Inter-IA chat | `true` | Uses Redis |
| `FEATURE_DISTRIBUTED_TRACING` | Tracing UIs | `true` | Enterprise recommended |
| `FEATURE_A_B_TESTING` | Experiment engine | `false` | Enterprise only |

---

## Environment Profiles

| Profile | File | Notes |
|---------|------|-------|
| Development | `.env.dev` | Verbose logs, debug enabled, mock credentials allowed |
| Staging | `.env.staging` | Mirrors production with lower scale; use masked credentials |
| Production | `.env.prod` | Debug disabled, strict security settings, secrets injected at runtime |
| Testing | `.env.test` | Optional – use in CI for isolated DB/Redis |

**Recommendation:** store only non-sensitive defaults in git. For staging/prod, generate `.env.*` during deployment using secrets from Vault, AWS Secrets Manager, or similar.

---

## Validation Workflow

1. Copy template: `cp .env.example .env.dev`
2. Populate values manually or via script (see `./scripts/config/apply-env.sh`).
3. Run validation:
   - `./scripts/config/validate.sh --env .env.dev`
   - `./scripts/orchestrator/validate-activation-matrix.sh`
   - `./scripts/squad/validate-personas.sh --strict`
4. Start services: `docker-compose --env-file .env.dev up -d`
5. Run smoke test: `./scripts/troubleshooting/health-check.sh`

Document any overrides in `docs/CHANGELOG.md` or infrastructure runbooks.

---

## Secrets Management

- Use `.gitignore` to exclude `.env.*` files (already configured).
- For production, prefer a secrets manager (AWS Secrets Manager, Hashicorp Vault, Azure Key Vault).
- Inject secrets at runtime via container orchestrator (Kubernetes secrets, Docker swarm secrets, GitHub Actions secrets).
- Rotate credentials regularly (quarterly minimum) and update ledger entry when rotation completes.

---

## Troubleshooting Configuration

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| App fails to start with `Missing OPENAI_API_KEY` | Key not set | Add to `.env.*` or disable ML routing (`ROUTING_USE_ML=false`) |
| `psql: connection refused` | Wrong host/port | Use `postgres` host inside Docker network |
| Personas not loading | YAML invalid | Run `./scripts/squad/validate-personas.sh --strict --fix` |
| RAG search empty | `RAG_ENABLED=false` or Chroma unreachable | Enable flag or start container `docker-compose up chromadb` |
| Grafana login fails | Password changed but not updated | Set `GRAFANA_ADMIN_PASSWORD` and restart container |
| Rate limit triggered unexpectedly | `API_RATE_LIMIT_REQUESTS` too low | Increase value or use API key rotation |

---

## Appendix: Example Templates

### `.env.staging`
```
PROJECT_NAME=btv-staging
ENVIRONMENT=staging
DEBUG=false
OPENAI_MODEL=gpt-4o-mini
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=${STAGING_POSTGRES_PASSWORD}
REDIS_PASSWORD=${STAGING_REDIS_PASSWORD}
ORCHESTRATION_MODE=assisted
COST_DAILY_LIMIT=25.00
GRAFANA_ADMIN_PASSWORD=${STAGING_GRAFANA_PASSWORD}
AUTH_ENABLED=true
AUTH_JWT_SECRET=${STAGING_JWT_SECRET}
```

### `.env.prod`
```
PROJECT_NAME=btv-prod
ENVIRONMENT=production
DEBUG=false
FOUNDATION_LEVEL=enterprise
OPENAI_MODEL=gpt-4o
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=${PROD_POSTGRES_PASSWORD}
REDIS_PASSWORD=${PROD_REDIS_PASSWORD}
GRAFANA_ADMIN_PASSWORD=${PROD_GRAFANA_PASSWORD}
AUTH_ENABLED=true
AUTH_JWT_SECRET=${PROD_JWT_SECRET}
ENCRYPTION_ENABLED=true
ENCRYPTION_KEY=${PROD_ENCRYPTION_KEY}
FEATURE_A_B_TESTING=true
FEATURE_PREDICTIVE_CONFLICTS=true
COST_DAILY_LIMIT=75.00
COST_PER_DECISION_LIMIT=1.00
API_RATE_LIMIT_REQUESTS=600
API_RATE_LIMIT_BURST=120
```

Update this guide whenever new configuration options are introduced or defaults change.
