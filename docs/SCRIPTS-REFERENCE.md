# 🔧 BuildToValue v7.0 – Scripts Reference

Complete reference for every script shipped with BuildToValue v7. Use this guide as a living catalog when you need to understand what automation already exists before writing a new one.

> **Tip:** all scripts accept `--help` for usage details and support verbose output via `--verbose`.

---

## 📂 Directory Map

```
scripts/
├── orchestrator/         # Routing, handoffs, autonomy and squad operations
├── squad/                # Persona lifecycle management
├── learning/             # Auto-RAG and lessons learned
├── monitoring/           # Metrics, dashboards, benchmarking
├── ledger/               # Decision ledger & ADR automation
├── database/             # Schema, migrations, backups
├── gates/                # Quality gates entry points
├── migration/            # v6 → v7 migration helpers
├── troubleshooting/      # Diagnostics, health checks, support bundles
├── config/               # Environment & activation matrix tooling
├── tutorials/            # Interactive onboarding flows
└── utils/                # Shared helpers invoked by other scripts
```

---

## 🧭 Quick Navigation

| Category | Primary Scripts | Core Use-Cases |
|----------|-----------------|----------------|
| Orchestrator | 15 scripts | Route problems, manage handoffs, autonomy control |
| Squad | 12 scripts | Validate, reload, customise personas |
| Learning | 10 scripts | Auto-RAG lifecycle, indexing, optimisation |
| Monitoring | 14 scripts | Dashboards, benchmarks, alert management |
| Ledger | 8 scripts | Decision capture, ADR generation, reporting |
| Database | 9 scripts | Schema, migrations, backups & restores |
| Quality Gates | 6 scripts | Run and validate BuildToValue gates |
| Migration | 7 scripts | Export/import v6 data, schema alignment |
| Troubleshooting | 11 scripts | Diagnostics, health checks, support bundles |
| Utilities | 8 scripts | Helpers (formatting, token usage, linting) |

---

## 1. Orchestrator Scripts

### `orchestrator/route-problem.sh`
Routes a problem statement through the activation matrix to recommend (or execute) an IA squad.

```
./scripts/orchestrator/route-problem.sh "How should we implement OAuth2?" \
  --context-file=./docs/requirements/auth.md \
  --mode=assisted \
  --min-confidence=0.8 \
  --max-cost=0.35
```

Key options:
- `--context` / `--context-file`: JSON payload or file with additional signals.
- `--ias` / `--exclude`: limit the candidate personas.
- `--execute`: auto-execute if confidence ≥ threshold.
- `--dry-run`: preview routing without activating personas.

Returns a detailed recommendation with costs, timeline, supporting personas, and asks whether to execute immediately.

---

### `orchestrator/activate-ia.sh`
Manually trigger a single IA with rich context.

```
./scripts/orchestrator/activate-ia.sh ia-developer \
  --task="Refactor billing service" \
  --context='{"files": ["services/billing.py"], "current_coverage": 42}' \
  --urgency=high \
  --timeout=5400
```

Use when you want to bypass routing and speak directly with a persona. Supports budgets, urgency levels, and context attachments.

---

### `orchestrator/activate-squad.sh`
Launch a multi-IA collaboration, optionally in parallel.

```
./scripts/orchestrator/activate-squad.sh \
  --primary=ia-product-manager \
  --support=ia-business-analyst,ia-designer,ia-developer \
  --task="Design and implement onboarding funnel" \
  --parallel
```

---

### `orchestrator/handoff.sh`
Formalise CIIF-compliant handoffs.

```
./scripts/orchestrator/handoff.sh \
  --from=ia-arquiteto \
  --to=ia-developer \
  --artifacts="docs/ADR-012.md,diagrams/auth-seq.puml" \
  --context="Architecture approved, implement service" \
  --ciif-file=.buildtovalue/orchestration/handoff-templates/standard.yaml
```

Supports broadcasting (`--broadcast`) and automatic deadline tracking.

---

### `orchestrator/consult.sh`
Peer-to-peer consultation across personas.

```
./scripts/orchestrator/consult.sh \
  --from=ia-developer \
  --to=ia-arquiteto \
  --question="Ideal caching strategy for 50k products?" \
  --context='{"traffic": "read-heavy", "update_frequency": "daily"}'
```

---

### Additional orchestrator utilities
- `set-mode.sh` – Toggle orchestration between `manual`, `assisted`, `autonomous`.
- `set-autonomy.sh` – Adjust IA autonomy level (supports temporary overrides).
- `autonomy-status.sh` – Snapshot of all autonomy levels and performance grades.
- `squad-status.sh` – Availability view with active tasks per persona.
- `active-tasks.sh` – Show in-flight work, owners, SLAs.
- `active-handoffs.sh` / `track-handoff.sh` – Monitor handoff lifecycle.
- `resolve-conflict.sh` – Execute conflict resolution protocol Levels 1-4.
- `alert.sh` / `broadcast.sh` / `suggest.sh` – Communication tooling between personas.

---

## 2. Squad Management Scripts

### `squad/validate-personas.sh`
Validates persona YAML files, checking schema, activation triggers, and references.

```
./scripts/squad/validate-personas.sh --strict --fix
```

### `squad/reload-personas.sh`
Reload persona configurations into the runtime orchestrator cache.

```
./scripts/squad/reload-personas.sh --ia=ia-qa
```

### `squad/test-persona.sh`
Run a dry-run activation to confirm persona alignment.

```
./scripts/squad/test-persona.sh ia-auditor "Review OAuth threat model"
```

### `squad/customize-persona.sh`
Interactive wizard to specialise a persona for a new domain.

### Other squad helpers
`list-personas.sh`, `persona-info.sh`, `add-reference.sh`, `clone-persona.sh`, `export-persona.sh`, `import-persona.sh`, `reset-persona.sh`, `squad-composition.sh`.

---

## 3. Learning System Scripts

### `learning/create-rag-collection.sh`
Bootstrap a ChromaDB collection (distance metric, persistence, reset mode).

### `learning/index-decisions.sh`
Index ledger decisions or ADRs into the RAG store. Supports incremental mode.

```
./scripts/learning/index-decisions.sh --source=.buildtovalue/ledger/2025-Q1/ --incremental
```

### `learning/test-rag-search.sh`
Validate retrieval quality.

```
./scripts/learning/test-rag-search.sh "Blue/green deployment" --max-results=8 --threshold=0.82
```

### `learning/capture-lesson.sh`
Manual lessons learned capture with significance, tags, and optional linked decisions.

### Optimisation utilities
`optimize-rag-index.sh`, `prune-rag-collection.sh`, `rebuild-embeddings.sh`, `auto-train-routing.sh` (updates ML routing model using ledger feedback).

#### `validate-rag-accuracy.sh`
Validate RAG retrieval accuracy to ensure the right decisions and lessons are surfaced.

```
./scripts/learning/validate-rag-accuracy.sh
```

#### `import-historical-decisions.sh`
Bring legacy ledger data (for example v6 exports) into the v7 learning system.

```
./scripts/learning/import-historical-decisions.sh \
  --source=v6-decisions.jsonl
```

#### `export-lessons-learned.sh`
Publish the current lessons learned repository to Markdown for quarterly reviews or compliance.

```
./scripts/learning/export-lessons-learned.sh \
  --output=lessons-2025-q1.md \
  --period=last-quarter
```

#### `rag-statistics.sh`
Summarise the current RAG index state (documents, embeddings, freshness).

```
./scripts/learning/rag-statistics.sh
```

#### `clear-rag-cache.sh`
Flush cached RAG retrieval results when tuning similarity thresholds or after large imports.

```
./scripts/learning/clear-rag-cache.sh
```

---

## 4. Monitoring & Observability Scripts

### `monitoring/squad-dashboard.sh`
Real-time squad dashboard (terminal UI) to observe IA activity, costs, and current workloads.

```
./scripts/monitoring/squad-dashboard.sh [OPTIONS]
```

Key parameters:
- `--refresh` (seconds, default `5`)
- `--compact` (toggle condensed layout)

Example invocations:
- `./scripts/monitoring/squad-dashboard.sh`
- `./scripts/monitoring/squad-dashboard.sh --refresh=2`
- `./scripts/monitoring/squad-dashboard.sh --compact`

### `monitoring/performance-metrics.sh`
Generate performance summaries for a period or persona, supporting text/JSON output.

```
./scripts/monitoring/performance-metrics.sh [OPTIONS]
```

Common options:
- `--period` (`today`, `yesterday`, `last-week`, `last-month`, `last-quarter`)
- `--ia`
- Custom range via `--from` / `--to`
- `--format` (`text`, `json`)

### `monitoring/cost-analysis.sh`
Analyse FinOps trends with optional breakdowns and forward-looking forecasts.

```
./scripts/monitoring/cost-analysis.sh [OPTIONS]
```

Useful switches:
- `--period` (default `last-month`)
- `--breakdown`
- `--forecast`

### `monitoring/health-check.sh`
Full-stack health check (also listed in troubleshooting) returning status, warnings, and remediation hints.

```
./scripts/monitoring/health-check.sh [OPTIONS]
```

### `monitoring/import-dashboards.sh`
Import Grafana dashboards individually or en masse.

```
./scripts/monitoring/import-dashboards.sh [OPTIONS]
```

Options:
- `--dashboard`
- `--all`

### `monitoring/configure-alerts.sh`
Wire alert destinations (Slack, email) and tune severity thresholds.

```
./scripts/monitoring/configure-alerts.sh [OPTIONS]
```

Parameters:
- `--slack-webhook`
- `--email`
- `--threshold` (default `critical`)

### Other monitoring helpers
- `identify-bottlenecks.sh` – Analyse performance bottlenecks with prioritised recommendations.
- `optimize-ia.sh` – Focus optimisation efforts on a single IA.
- `benchmark-routing.sh` – Benchmark routing performance (`--iterations`).
- `ab-test-routing.sh` – Compare routing strategies.
- `export-metrics.sh` – Export metrics for archival/BI tooling.
- `squad-health.sh` – Quick health snapshot.
- `monthly-report.sh` – Generate executive PDF reports.
- `improvement-report.sh` – Recommend improvements for the chosen period.
- `apply-optimizations.sh` – Execute recommendations (supports `--auto-approve=false`).

---

## 5. Ledger & Governance Scripts

### `ledger/recent-decisions.sh`
List recent decisions with rich filtering and multiple output formats.

```
./scripts/ledger/recent-decisions.sh [OPTIONS]
```

Key flags: `--limit`, `--ia`, `--success`, `--format` (`table`, `json`).

### `ledger/search.sh`
Full-text or filtered search across the decision ledger.

```
./scripts/ledger/search.sh [OPTIONS]
```

Filters include `--query`, `--ia`, `--type`, `--period`, `--keywords`, and `--success`.

### `ledger/trace-decision.sh`
Inspect the lifecycle of a single decision including routing, confidence, and completion details.

```
./scripts/ledger/trace-decision.sh DECISION_ID [OPTIONS]
```

Supports `--detailed` and `--artifacts`.

### `ledger/generate-adr.sh`
Convert a ledger decision into an ADR using the configured template.

```
./scripts/ledger/generate-adr.sh [OPTIONS]
```

Important options: `--decision-id`, `--output`, `--template`.

### `ledger/auto-generate-adrs.sh`
Bulk-generate ADRs based on significance and timeframe.

```
./scripts/ledger/auto-generate-adrs.sh [OPTIONS]
```

Parameters: `--period`, `--min-significance`, `--commit`.

### `ledger/analytics.sh`
Produce analytics and trends for ledger activity.

```
./scripts/ledger/analytics.sh [OPTIONS]
```

Flags: `--period`, `--ia`, `--format`.

### `ledger/export.sh`
Export ledger data to CSV/JSON/XLSX for external analysis.

```
./scripts/ledger/export.sh [OPTIONS]
```

Arguments: `--format`, `--period`, `--output`.

### `ledger/show-last-routing.sh`
Peek at the most recent routing decision for quick diagnostics.

```
./scripts/ledger/show-last-routing.sh
```

---

## 6. Database Scripts

### `database/backup.sh`
Create a full backup (PostgreSQL, ChromaDB, Redis) with optional compression and custom destinations.

```
./scripts/database/backup.sh [OPTIONS]
```

Options: `--output`, `--compress`, `--include-rag`.

### `database/restore.sh`
Restore from a previously generated backup archive.

```
./scripts/database/restore.sh BACKUP_FILE [OPTIONS]
```

Supports `--confirm` and `--include-rag`.

### `database/migrate.sh`
Apply database migrations to the latest or a specific target.

```
./scripts/database/migrate.sh [OPTIONS]
```

Flags: `--to`, `--dry-run`.

### `database/test-connection.sh`
Smoke-test connectivity to PostgreSQL, Redis, and ChromaDB.

```
./scripts/database/test-connection.sh
```

### Other database utilities
- `init-schema.sh`
- `seed-data.sh`
- `vacuum.sh`
- `check-integrity.sh`
- `list-backups.sh`

---

## 7. Quality Gates Scripts

### `gates-v7.sh`
Primary entry point to run BuildToValue quality gates with flexible scope selection.

```
./scripts/gates-v7.sh [OPTIONS]
```

Options include `--full`, `--foundation`, `--squad`, `--business`, `--learning`, `--exclude`, `--strict`, and `--report`.

### `gates/validate-gates-config.sh`
Validate the configuration powering quality gates.

```
./scripts/gates/validate-gates-config.sh
```

### `gates/update-thresholds.sh`
Adjust specific gate thresholds from the command line.

```
./scripts/gates/update-thresholds.sh [OPTIONS]
```

Arguments: `--gate`, `--threshold`.

### Other quality gate scripts
- `gates-history.sh`
- `gates-trend.sh`
- `custom-gate.sh`

---

## 8. Migration Scripts (v6 → v7)

### `migrate-v6-to-v7.sh`
Main migration orchestrator. Supports interactive and automated execution modes with optional backups and validation skips.

```
./scripts/migrate-v6-to-v7.sh [OPTIONS]
```

### `rollback-to-v6.sh`
Rollback script for reverting the environment to v6.

```
./scripts/rollback-to-v6.sh [OPTIONS]
```

### Other migration helpers
- `migration/backup-v6-state.sh`
- `migration/export-v6-data.sh`
- `migration/import-to-v7.sh`
- `migration/verify-data-integrity.sh`
- `migration/add-mental-models.sh`
- `migration/update-consensus-schema.sh`

---

## 9. Troubleshooting Scripts

### `troubleshooting/health-check.sh`
Comprehensive system health check mirroring monitoring output with optional verbose/JSON modes.

```
./scripts/troubleshooting/health-check.sh [OPTIONS]
```

### `troubleshooting/diagnostic-report.sh`
Generate an in-depth diagnostic report optionally embedding recent logs.

```
./scripts/troubleshooting/diagnostic-report.sh [OPTIONS]
```

### `troubleshooting/generate-support-bundle.sh`
Produce a zipped support bundle containing logs, configs, database schema snapshots, and recent decisions.

```
./scripts/troubleshooting/generate-support-bundle.sh
```

### Other troubleshooting utilities
- `ia-diagnostic.sh`
- `routing-confidence.sh`
- `handoff-analysis.sh`
- `conflict-patterns.sh`
- `performance-diagnostic.sh`
- `test-emergency-procedures.sh`
- `autonomy-audit.sh`
- `review-decisions.sh`

---

## 10. Utility Scripts

### `init-v7.sh`
Initialise a fresh BuildToValue v7 project according to the onboarding checklist.

```
./scripts/init-v7.sh
```

### `config/validate.sh`
Validate configuration files, optionally auto-fixing common mistakes.

```
./scripts/config/validate.sh [OPTIONS]
```

Flags: `--config`, `--fix`.

### `format/format-ledger.sh`
Format ledger files into human-readable or machine-friendly outputs.

```
./scripts/format/format-ledger.sh INPUT_FILE [OPTIONS]
```

Options: `--format` (`table`, `json`, `markdown`), `--output`.

### `utils/json-to-yaml.sh`
Convert JSON files to YAML.

```
./scripts/utils/json-to-yaml.sh INPUT.json OUTPUT.yaml
```

### `utils/yaml-to-json.sh`
Convert YAML documents to JSON.

```
./scripts/utils/yaml-to-json.sh INPUT.yaml OUTPUT.json
```

### Other utilities
- `clean.sh`
- `reset-demo.sh`
- `export-config.sh`
- `import-config.sh`

---

## ✅ Best Practices

1. Prefer the provided scripts over manual operations to maintain auditability.
2. Always run `validate-personas.sh` and `validate-activation-matrix.sh` after edits.
3. Use `--dry-run` flags in production environments before executing impactful scripts.
4. Pipe outputs to JSON/CSV and commit results when they influence decision-making.
5. Update this reference whenever new automation is added to keep the catalog trustworthy.

Need a script that is missing? Open an issue or contribute via `docs/CONTRIBUTING.md`.
