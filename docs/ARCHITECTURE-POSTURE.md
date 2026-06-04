# Postura Arquitetural — ConciliaIA

> "Ferramenta funcional em Docker, escalável por design."
> Definições fixadas para o vocabulário do projeto.

## Definições

- **"Docker único" = uma imagem da APLICAÇÃO (frontend estático + FastAPI) + banco EXTERNO ao container.**
  - Regra inegociável: **PostgreSQL nunca dentro do container da aplicação.** Fica
    como serviço separado no `docker-compose` (com healthcheck) ou DB gerenciado.
    Empacota-se o app/binário web, **não o estado** — preserva durabilidade,
    backup, restore e operação segura.
  - Estado atual: `Dockerfile` constrói o frontend (Vite) e o backend numa única
    imagem; o FastAPI serve o build estático (`FRONTEND_DIST`). O `docker-compose.yml`
    mantém o Postgres como serviço à parte.

- **"Escalável por design" = modular, observável e pronto para extração futura.**
  Não significa distribuir agora. Significa fronteiras de módulo limpas, API
  versionada/consistente (`/api/v1`, incl. `/api/v1/auth`), observabilidade com
  `request_id` (header `X-Request-ID` + envelope de erro `{detail, error_code,
  request_id}`), contrato de erros estável e pontos de extensão (acquirers/DMN)
  que permitam extrair um módulo para serviço próprio **quando** as métricas
  justificarem — sem reescrever a base.

- **"Orquestração de processo agora" = job table + worker leve, NÃO BPMS.**
  A reconciliação assíncrona usa a tabela `reconciliation_jobs` + worker
  in-process (`asyncio`). Camunda/Zeebe/Temporal, Kafka/RabbitMQ e process mining
  são **backlog estratégico**, adotados só sob evidência de gargalo (métricas de
  `/api/v1/reconciliation-jobs/metrics`). Complexidade prematura é o maior risco.

- **Precisão financeira** já garantida no DB (`Numeric(15,2)`) e no domínio
  (`Money`/`Decimal`). Corrigida apenas a fronteira de serialização (Pydantic
  `Decimal` via `MoneyAmount`, emitido como número JSON), **sem `ALTER TABLE`**.

## Observabilidade

- Toda resposta carrega `X-Request-ID`; erros seguem o envelope
  `{detail, error_code, request_id}` (`src/api/errors.py`).
- Métricas de processo em `GET /api/v1/reconciliation-jobs/metrics`:
  duração p50/p95, throughput de matches (30d), backlog de divergências e taxa
  de auto-approval.

## Extensibilidade

- `GET /api/v1/acquirers` é autodescritivo e lê o registro plugável
  (`src/infrastructure/acquirers/registry.py`). Onboarding de um novo
  adquirente/formato = registrar a classe de parser.
- Decisão table-driven (DMN leve) em `src/application/services/decision_table.py`,
  exposta em `GET /api/v1/reconciliation-rules`. O limiar de auto-approval (0.95)
  e os SLAs por severidade são externalizáveis por tenant via
  `tenant.features['reconciliation_policy']`.

## Backlog estratégico (ativar só sob evidência das métricas)

- Event-driven (Redis Streams → Kafka) e/ou BPMS (Camunda/Zeebe/Temporal).
- Process mining.
- Wiring per-tenant do `decision_table` diretamente no motor de matching.

## Fora de escopo imediato (backlog funcional)

- `/settings` backend + ligar `SettingsPage` (hoje mock) e `/users/me`.
- WebSocket/SSE para notifications e para o progresso de jobs (hoje: polling).
- Tela Cielo dedicada; consumo dos exports em Excel.
- E2E Playwright no CI.
