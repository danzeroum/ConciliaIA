# Documentação — ConciliaIA

Índice da documentação do projeto. (Início rápido e visão geral ficam no
[`README.md`](../README.md) da raiz.)

## Essenciais

| Doc | Conteúdo |
|---|---|
| [`ARCHITECTURE-POSTURE.md`](ARCHITECTURE-POSTURE.md) | Postura arquitetural: "Docker único" (app + Postgres externo), "escalável por design", orquestração com job table, backlog estratégico. **Fonte da verdade da arquitetura.** |
| [`API-REFERENCE.md`](API-REFERENCE.md) | Referência da API (`/api/v1/*`), auth, envelope de erro, jobs assíncronos. |
| [`API-ENDPOINTS.md`](API-ENDPOINTS.md) | Nota específica do import EDI. |
| [`SECURITY.md`](SECURITY.md) | Modelo de segurança (auth, RBAC, rate limit, headers) e o que é backlog. |
| [`ACQUIRER_INTEGRATIONS.md`](ACQUIRER_INTEGRATIONS.md) | Adquirentes e o registro plugável de parsers (`/api/v1/acquirers`). |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de mudanças. |

## Negócio e UX

| Doc | Conteúdo |
|---|---|
| [`business/`](business/) | Glossário, regras de negócio, modelo de domínio, user stories. |
| [`ux/`](ux/) | Personas, princípios de UX, especificação de componentes, acessibilidade. |
| [`FRONTEND-SPECIFICATION.md`](FRONTEND-SPECIFICATION.md) | Especificação do frontend (React/Vite/MUI). |

## Decisões de arquitetura (ADR)

| Doc | Conteúdo |
|---|---|
| [`ADR/ADR-002-architecture-decisions.md`](ADR/ADR-002-architecture-decisions.md) | Decisões de domínio (multi-tenancy, cascata de matching). _Parcialmente desatualizado na parte de infra._ |
| [`ADR/ADR-003-rede-torc-parser.md`](ADR/ADR-003-rede-torc-parser.md) | Parser Rede TORC. |

## Comunidade

| Doc | Conteúdo |
|---|---|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Guia de contribuição. |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Código de conduta. |

## Em revisão (desatualizados — não usar como fonte da verdade)

Estes docs ainda contêm referências a infraestrutura/processos que **não existem
mais** no código (ex.: Kubernetes, Prometheus/Grafana, orquestração legada).
Pendentes de reescrita ou remoção:

- `ARCHITECTURE-DIAGRAMS.md`, `RUNBOOK.md`, `HANDOFF-DOCUMENT.md`,
  `PERFORMANCE-TUNING.md`, `CONFIGURATION-GUIDE.md`.

> Para o estado real da arquitetura/operação, use `ARCHITECTURE-POSTURE.md` e o
> `README.md`.
