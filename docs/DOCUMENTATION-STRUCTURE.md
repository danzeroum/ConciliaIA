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

## Operação e configuração

| Doc | Conteúdo |
|---|---|
| [`RUNBOOK.md`](RUNBOOK.md) | Operação do deploy real (docker-compose, migrations, health, logs, troubleshooting). |
| [`CONFIGURATION-GUIDE.md`](CONFIGURATION-GUIDE.md) | Variáveis de ambiente (obrigatórias, opcionais e legadas). |

> Para a postura de arquitetura/operação, a fonte da verdade é
> [`ARCHITECTURE-POSTURE.md`](ARCHITECTURE-POSTURE.md) e o [`README.md`](../README.md).

