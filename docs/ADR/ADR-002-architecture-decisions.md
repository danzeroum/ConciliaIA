# ADR-002 – Architecture Decisions for ConciliaAI

- **Status:** Approved 2025-10-18
- **Context:** Multi-tenant financial reconciliation platform that must scale from 5 to 2,000+ tenants
- **Forces:** Cost efficiency for early phases, PCI-DSS and LGPD compliance, observability requirements, and evolutionary growth across five phases

## ADR-002.1 – Multi-Tenancy Strategy

- **Decision:** Adopt an evolutionary hybrid model. Start with pooled multi-tenancy (shared database with tenant partitioning) for phases 1-2, transition to hybrid pool + silo for phases 3-4, and move the majority of enterprise tenants to dedicated silos in phase 5.
- **Rationale:** Minimises cost in the early lifecycle while providing a clear path to isolation and scale for large tenants. Avoids up-front over-engineering yet preserves growth options.
- **Consequences:** Requires zero-downtime migration tooling, tenant-aware schema migrations, and observability that can trace activity across both pooled and siloed deployments.

## ADR-002.2 – Matching Strategy

- **Decision:** Implement a three-tier cascade combining exact, fuzzy, and machine learning matching approaches.
- **Rationale:** Exact matching delivers high throughput for the majority of records, fuzzy matching handles rounding and timing discrepancies, and ML captures complex outliers. This combination hits the 99.5% accuracy target while keeping per-transaction cost low.
- **Consequences:** Necessitates feature engineering for the ML tier, human-in-the-loop review below 0.95 confidence, and continuous evaluation of false positive/negative rates.

## ADR-002.3 – Security Architecture

- **Decision:** Enforce a seven-layer defence-in-depth model covering network segmentation, authentication and authorisation, encryption, secrets management, audit logging, application security, and incident response.
- **Rationale:** PCI-DSS Level 1 and LGPD compliance mandate strict controls. Breaches would be existential.
- **Consequences:** Requires coordinated IAM policies, automated secrets rotation, audit trail retention, proactive monitoring, and runbooks that support rapid isolation of compromised tenants.

## ADR-002.4 – Observability Strategy

- **Decision:** Ship the product with first-class logging, metrics, and tracing instrumentation. Use structlog for structured logs, Prometheus metrics for KPIs and technical health, and OpenTelemetry tracing integrated with Jaeger or AWS X-Ray.
- **Rationale:** Multi-tenant debugging is infeasible without rich observability. Early investment avoids costly retrofits.
- **Consequences:** Slight increase in latency and infrastructure spend (+5-10% latency, ~R$30/month) but dramatically improves supportability, alerting, and compliance reporting.

## Deployment Roadmap

- **Phase 1 – Alpha (1-5 tenants):** Single-task Fargate deployment, t4g.micro PostgreSQL, single-node Redis, single NAT gateway. Cost target ~R$150/month.
- **Phase 2 – Beta (10-50 tenants):** Aurora Serverless v2, multi-AZ Redis, auto-scaling ECS tasks, CloudWatch/X-Ray observability. Cost target ~R$465/month.
- **Phase 3 – Growth (100+ tenants):** Larger Aurora capacity, Redis cluster mode, CloudFront, Grafana, PagerDuty, and DataDog APM with multi-region disaster recovery. Cost target ~R$1,355/month.

## Next Steps

1. Complete ML-based matcher and anomaly detection services.
2. Build automated testing (unit, integration, load) with >85% coverage and 99.5% accuracy validation.
3. Finalise CI/CD, Terraform apply for Phase 1, and execute production smoke tests.
4. Coordinate with security and operations squads for penetration testing and observability dashboards.
