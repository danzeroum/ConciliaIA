# ConciliAI ⇄ BuildToValue v7.1 – Migration Plan (Programmatic)

- btv_version: 7.1.0
- timestamp: 2025-11-04T16:43:21.902513-03:00
- dry_run: False

## Items

| Action | Source | Target | Notes |
|---|---|---|---|
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\btv-local-executor.yml` | `.github/workflows/btv-local-executor.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\buildtovalue-gates.yml` | `.github/workflows/buildtovalue-gates.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\deploy-monitoring.yml` | `.github/workflows/deploy-monitoring.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\phase1-validation.yml` | `.github/workflows/phase1-validation.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\phase2-validation.yml` | `.github/workflows/phase2-validation.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\phase3-compliance.yml` | `.github/workflows/phase3-compliance.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\pipeline-bifido.yml` | `.github/workflows/pipeline-bifido.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\validate-ci-integrity.yml` | `.github/workflows/validate-ci-integrity.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\validate-orchestrator.yml` | `.github/workflows/validate-orchestrator.yml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.github\workflows\_btv-snippets.insert.md` | `.github/workflows/_btv-snippets.insert.md` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.pre-commit-config.yaml` | `.pre-commit-config.yaml` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.editorconfig` | `.editorconfig` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\.gitattributes` | `.gitattributes` |  |
| MERGE | `C:\BuldToValue\Migracao\BuildToValue\.gitignore` | `.gitignore` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\scripts\utils\common.sh` | `scripts/utils/common.sh` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\scripts\squad\validate-personas.sh` | `scripts/squad/validate-personas.sh` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\scripts\troubleshooting\health-check.sh` | `scripts/troubleshooting/health-check.sh` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates-v7.sh` | `scripts/gates-v7.sh` |  |
| REPLACE | `C:\BuldToValue\Migracao\BuildToValue\scripts\init-v7.sh` | `scripts/init-v7.sh` |  |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\analytics\calculate-roi.sh` | `scripts/btv/analytics/calculate-roi.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\analytics\collect-metrics.sh` | `scripts/btv/analytics/collect-metrics.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\analytics\get-best-ia-recommendation.sh` | `scripts/btv/analytics/get-best-ia-recommendation.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\analytics\track-ia-performance.sh` | `scripts/btv/analytics/track-ia-performance.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\architecture\generate-ownership-map.sh` | `scripts/btv/architecture/generate-ownership-map.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\auditor\quarantine-flaky.sh` | `scripts/btv/auditor/quarantine-flaky.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\auditor\run-bdd-validation.sh` | `scripts/btv/auditor/run-bdd-validation.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\auditor\run-mutation-tests.sh` | `scripts/btv/auditor/run-mutation-tests.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ci\patch-pytest-paths.sh` | `scripts/btv/ci/patch-pytest-paths.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ci\scan-script-references.sh` | `scripts/btv/ci/scan-script-references.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ci\test-phase3-local.sh` | `scripts/btv/ci/test-phase3-local.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\certification-packager.sh` | `scripts/btv/compliance/certification-packager.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\unified-compliance-scanner.sh` | `scripts/btv/compliance/unified-compliance-scanner.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\gdpr\breach-notification.sh` | `scripts/btv/compliance/frameworks/gdpr/breach-notification.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\gdpr\consent-manager.py` | `scripts/btv/compliance/frameworks/gdpr/consent-manager.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\gdpr\data-inventory.sh` | `scripts/btv/compliance/frameworks/gdpr/data-inventory.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\gdpr\dpia-generator.sh` | `scripts/btv/compliance/frameworks/gdpr/dpia-generator.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\gdpr\right-to-erasure.sh` | `scripts/btv/compliance/frameworks/gdpr/right-to-erasure.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\iso27001\isms-audit.sh` | `scripts/btv/compliance/frameworks/iso27001/isms-audit.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\iso27001\risk-assessment.py` | `scripts/btv/compliance/frameworks/iso27001/risk-assessment.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\iso27001\risk-matrix-generator.sh` | `scripts/btv/compliance/frameworks/iso27001/risk-matrix-generator.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\sox\audit-trail-validator.sh` | `scripts/btv/compliance/frameworks/sox/audit-trail-validator.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\compliance\frameworks\sox\change-control.py` | `scripts/btv/compliance/frameworks/sox/change-control.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\development\generate-tests.sh` | `scripts/btv/development/generate-tests.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\development\harden-immediately.sh` | `scripts/btv/development/harden-immediately.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\development\validate-invariants.sh` | `scripts/btv/development/validate-invariants.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\fixes\fix-dependency-httpx.sh` | `scripts/btv/fixes/fix-dependency-httpx.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\ai-rework-rate.sh` | `scripts/btv/gates/ai-rework-rate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\budget-compliance.sh` | `scripts/btv/gates/budget-compliance.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\confidence-accuracy.sh` | `scripts/btv/gates/confidence-accuracy.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\contract-compliance.sh` | `scripts/btv/gates/contract-compliance.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\contract-coverage.sh` | `scripts/btv/gates/contract-coverage.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\contract-validation.sh` | `scripts/btv/gates/contract-validation.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\documentation-check.sh` | `scripts/btv/gates/documentation-check.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\flaky-test-rate.sh` | `scripts/btv/gates/flaky-test-rate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\ia-quality-metrics.sh` | `scripts/btv/gates/ia-quality-metrics.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\override-rate.sh` | `scripts/btv/gates/override-rate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\plan-approval-rate.sh` | `scripts/btv/gates/plan-approval-rate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\token-efficiency.sh` | `scripts/btv/gates/token-efficiency.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\gates\what-matters-gate.sh` | `scripts/btv/gates/what-matters-gate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\governance\mpaa-validator.py` | `scripts/btv/governance/mpaa-validator.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\governance\prompt-integrity-checker.sh` | `scripts/btv/governance/prompt-integrity-checker.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\governance\prompt-signer.py` | `scripts/btv/governance/prompt-signer.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ia-assisted\manage-workflow.sh` | `scripts/btv/ia-assisted/manage-workflow.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ia-assisted\setup-aliases.sh` | `scripts/btv/ia-assisted/setup-aliases.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ledger\auto-log-decision.sh` | `scripts/btv/ledger/auto-log-decision.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ledger\export.sh` | `scripts/btv/ledger/export.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ledger\log-prompt.sh` | `scripts/btv/ledger/log-prompt.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ledger\search-prompts.sh` | `scripts/btv/ledger/search-prompts.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\ledger\upload-quality-report.sh` | `scripts/btv/ledger/upload-quality-report.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\maintenance\auto-maintenance.sh` | `scripts/btv/maintenance/auto-maintenance.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\maintenance\cleanup-archives.sh` | `scripts/btv/maintenance/cleanup-archives.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\maintenance\ledger-health-check.sh` | `scripts/btv/maintenance/ledger-health-check.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\maintenance\rotate-ledger.sh` | `scripts/btv/maintenance/rotate-ledger.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\metrics\compute-what-matters.sh` | `scripts/btv/metrics/compute-what-matters.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\metrics\export-prometheus.sh` | `scripts/btv/metrics/export-prometheus.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\metrics\render-wmm-report.js` | `scripts/btv/metrics/render-wmm-report.js` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\monitoring\github-metrics-simulator.py` | `scripts/btv/monitoring/github-metrics-simulator.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\monitoring\setup-alerts.sh` | `scripts/btv/monitoring/setup-alerts.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\grafana-dashboard.json` | `scripts/btv/observability/grafana-dashboard.json` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\metrics-collector.sh` | `scripts/btv/observability/metrics-collector.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\otel-collector.sh` | `scripts/btv/observability/otel-collector.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\span-exporter.sh` | `scripts/btv/observability/span-exporter.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\telemetry-config.yaml` | `scripts/btv/observability/telemetry-config.yaml` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\observability\tracer.py` | `scripts/btv/observability/tracer.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\gate-zero-validation.sh` | `scripts/btv/patches/gate-zero-validation.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\integration-test-ledger.sh` | `scripts/btv/patches/integration-test-ledger.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\master-execution.sh` | `scripts/btv/patches/master-execution.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-a-postgres-migration.sh` | `scripts/btv/patches/patch-a-postgres-migration.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-b-harmonization.sh` | `scripts/btv/patches/patch-b-harmonization.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-c-gui-contracts.sh` | `scripts/btv/patches/patch-c-gui-contracts.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-d-governance-resilience.sh` | `scripts/btv/patches/patch-d-governance-resilience.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-e-add-planning-policy.sh` | `scripts/btv/patches/patch-e-add-planning-policy.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-f-governance-validation-fallback.sh` | `scripts/btv/patches/patch-f-governance-validation-fallback.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\patch-g-add-enabled-flag.sh` | `scripts/btv/patches/patch-g-add-enabled-flag.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\patches\verification-post-patches.sh` | `scripts/btv/patches/verification-post-patches.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\pipeline\async-quality-audit.sh` | `scripts/btv/pipeline/async-quality-audit.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\pipeline\sync-quality-gate.sh` | `scripts/btv/pipeline/sync-quality-gate.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\planning\approve-plan.sh` | `scripts/btv/planning/approve-plan.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\planning\create-plan.sh` | `scripts/btv/planning/create-plan.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\planning\validate-plan.sh` | `scripts/btv/planning/validate-plan.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\providers\ia-provider-manager.sh` | `scripts/btv/providers/ia-provider-manager.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\providers\providers.yaml` | `scripts/btv/providers/providers.yaml` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\quality\static-analysis.sh` | `scripts/btv/quality/static-analysis.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\basic-scan.sh` | `scripts/btv/security/basic-scan.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\capability-manager.sh` | `scripts/btv/security/capability-manager.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\resource-limiter.sh` | `scripts/btv/security/resource-limiter.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\seccomp-profiles\default.json` | `scripts/btv/security/seccomp-profiles/default.json` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\seccomp-profiles\permissive.json` | `scripts/btv/security/seccomp-profiles/permissive.json` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\security\seccomp-profiles\strict.json` | `scripts/btv/security/seccomp-profiles/strict.json` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\slo\sli-calculator.sh` | `scripts/btv/slo/sli-calculator.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\slo\slo-reporter.py` | `scripts/btv/slo/slo-reporter.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\slo\slos.yaml` | `scripts/btv/slo/slos.yaml` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\slo\slo_reporter.py` | `scripts/btv/slo/slo_reporter.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\slo\__init__.py` | `scripts/btv/slo/__init__.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\specification\create-contract.sh` | `scripts/btv/specification/create-contract.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\specification\validate-contract.sh` | `scripts/btv/specification/validate-contract.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\testing\quarantine-flaky.sh` | `scripts/btv/testing/quarantine-flaky.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\testing\run-bdd-validation.sh` | `scripts/btv/testing/run-bdd-validation.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\testing\run-critical-tests.sh` | `scripts/btv/testing/run-critical-tests.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\testing\run-mutation-tests.sh` | `scripts/btv/testing/run-mutation-tests.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\testing\smart-retry.sh` | `scripts/btv/testing/smart-retry.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\tools\calculate-policy-checksums.sh` | `scripts/btv/tools/calculate-policy-checksums.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\tools\generate-scripts-reference.sh` | `scripts/btv/tools/generate-scripts-reference.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\learning\test-rag-search.sh` | `scripts/btv/learning/test-rag-search.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\btv-task.sh` | `scripts/btv/orchestrator/btv-task.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\execute-plan.sh` | `scripts/btv/orchestrator/execute-plan.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\ia-fallback-handler.sh` | `scripts/btv/orchestrator/ia-fallback-handler.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\sandbox-executor.sh` | `scripts/btv/orchestrator/sandbox-executor.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\smart-context.sh` | `scripts/btv/orchestrator/smart-context.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\sync-ledger-to-codex.sh` | `scripts/btv/orchestrator/sync-ledger-to-codex.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\orchestrator\task-lock-manager.sh` | `scripts/btv/orchestrator/task-lock-manager.sh` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\troubleshooting\diagnose_btv.py` | `scripts/btv/troubleshooting/diagnose_btv.py` | namespace scripts/btv |
| ADD-AS-NEW | `C:\BuldToValue\Migracao\BuildToValue\scripts\troubleshooting\check-container-env.sh` | `scripts/btv/troubleshooting/check-container-env.sh` | namespace scripts/btv |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\ethics\bias_analyzer.py` | `src/ethics/bias_analyzer.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\ethics\fairness_validator.py` | `src/ethics/fairness_validator.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\ethics\guardian.py` | `src/ethics/guardian.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\ethics\pii_detector.py` | `src/ethics/pii_detector.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\ethics\slo.py` | `src/ethics/slo.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\monitoring\metrics.py` | `src/monitoring/metrics.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\quality\intelligence\AdaptiveQualityGates.py` | `src/quality/intelligence/AdaptiveQualityGates.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\artifacts_analyzer.py` | `src/artifacts_analyzer.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\code_extractor.py` | `src/code_extractor.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\orchestrator.py` | `src/orchestrator.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\src\project_generator.py` | `src/project_generator.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\ci\test-phase3-local.sh` | `tests/ci/test-phase3-local.sh` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\ci\test_script_scanner.py` | `tests/ci/test_script_scanner.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\ci\test_workflow_consistency.py` | `tests/ci/test_workflow_consistency.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\compliance\test_gdpr_compliance.py` | `tests/compliance/test_gdpr_compliance.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\compliance\test_iso27001_compliance.py` | `tests/compliance/test_iso27001_compliance.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\compliance\test_sox_compliance.py` | `tests/compliance/test_sox_compliance.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\compliance\test_unified_scanner.py` | `tests/compliance/test_unified_scanner.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\devops\test_dependency_drift.py` | `tests/devops/test_dependency_drift.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\ethics\test_ethics_slo_smoke.py` | `tests/ethics/test_ethics_slo_smoke.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\ethics\test_pii_detector_smoke.py` | `tests/ethics/test_pii_detector_smoke.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\governance\test_ledger_integrity.py` | `tests/governance/test_ledger_integrity.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\governance\test_script_permissions.py` | `tests/governance/test_script_permissions.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\monitoring\test_metrics_smoke.py` | `tests/monitoring/test_metrics_smoke.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_api_contracts.py` | `tests/test_api_contracts.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_code_extractor.py` | `tests/test_code_extractor.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_concurrency_control.py` | `tests/test_concurrency_control.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_ethics_guardian.py` | `tests/test_ethics_guardian.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_ledger_rotation.py` | `tests/test_ledger_rotation.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_project_generator.py` | `tests/test_project_generator.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_prompt_contracts.py` | `tests/test_prompt_contracts.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_prompt_integrity.py` | `tests/test_prompt_integrity.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_resource_limits.py` | `tests/test_resource_limits.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_seccomp_profiles.py` | `tests/test_seccomp_profiles.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_slo_compliance.py` | `tests/test_slo_compliance.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\tests\test_telemetry_integration.py` | `tests/test_telemetry_integration.py` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\templates\plans\backend-service.json` | `templates/plans/backend-service.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\templates\plans\frontend-component.json` | `templates/plans/frontend-component.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\templates\pr\pull_request_template_v7.1.md` | `templates/pr/pull_request_template_v7.1.md` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\templates\specifications\jsonschema-template.json` | `templates/specifications/jsonschema-template.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\templates\specifications\openapi-rest-api.yaml` | `templates/specifications/openapi-rest-api.yaml` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\contracts\operator-gui\telemetry.json` | `contracts/operator-gui/telemetry.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\chromadb\.dockerignore` | `docker/chromadb/.dockerignore` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\chromadb\Dockerfile` | `docker/chromadb/Dockerfile` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\grafana\dashboards\ethics-slo.json` | `docker/grafana/dashboards/ethics-slo.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\grafana\provisioning\dashboards\quality-intelligence.json` | `docker/grafana/provisioning/dashboards/quality-intelligence.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\grafana\provisioning\datasources\prometheus.yml` | `docker/grafana/provisioning/datasources/prometheus.yml` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\prometheus\prometheus.yml` | `docker/prometheus/prometheus.yml` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\prometheus\rules\ethics_slo.rules.yml` | `docker/prometheus/rules/ethics_slo.rules.yml` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker\prometheus\rules\quality-intelligence.rules` | `docker/prometheus/rules/quality-intelligence.rules` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\monitoring\dashboards\what-matters.json` | `monitoring/dashboards/what-matters.json` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\docker-compose.quality-intelligence.yml` | `docker-compose.quality-intelligence.yml` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\Dockerfile.monitoring` | `Dockerfile.monitoring` |  |
| ADD | `C:\BuldToValue\Migracao\BuildToValue\SCRIPTS-REFERENCE.md` | `SCRIPTS-REFERENCE.md` |  |
| MERGE | `C:\BuldToValue\Migracao\BuildToValue\Makefile` | `Makefile` |  |
| MERGE | `C:\BuldToValue\Migracao\BuildToValue\.env.example` | `.env.example` |  |
| MERGE | `C:\BuldToValue\Migracao\BuildToValue\docker-compose.yml` | `docker-compose.yml` |  |

