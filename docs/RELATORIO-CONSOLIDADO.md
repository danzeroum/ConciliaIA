# Relatório Consolidado — ConciliaIA

> **Versão:** 1.0 · **Data:** 2026-06-09  
> **Base:** 6 relatórios técnicos de analistas + validação direta no código e nas issues do GitHub.  
> **Branch de entrega:** `claude/epic-gates-nniqsj`

---

## 1. Visão consolidada dos analistas

### Onde os 6 analistas **convergem** (e o código confirma)

- **Arquitetura é o ponto forte:** monólito modular limpo (camadas `api / application / domain / infrastructure`), DDD leve, padrão Strategy para matching, precisão financeira correta (`Numeric(15,2)` + value objects `Money` / `Decimal`).
- **Documentação acima da média:** 24 documentos em `docs/` (ARCHITECTURE-POSTURE, SECURITY, API-REFERENCE, ADRs, business/, ux/).
- **"IA" não é IA:** o motor é 100% determinístico (regras + heurística ponderada). O `MLMatcher` é um *placeholder*. Convergência total entre R2–R6; confirmado no código.
- **Lacunas recorrentes:** sem trilha de auditoria, sem LGPD em código, polling em vez de SSE, worker/scheduler in-process limitam escala, sem observabilidade (Prometheus/OTEL).

### Onde os analistas **divergem** (resolvido pela verdade do código)

| Tema | Divergência | Veredito (código / GitHub) |
|---|---|---|
| Acesso ao código | R1 afirma "código não acessível" e analisa só docs | **Código é público e acessível.** Ressalvas do R1 são improcedentes |
| RBAC | R2–R5: "implementado/aplicado"; R6: "definido mas não usado" | **R6 correto:** `require_roles` existe e é chamado **zero vezes** |
| Postura de segurança | R1/R3: "sólida / defesa em 7 camadas" | **Otimista demais.** RBAC nulo, token em localStorage, logout no-op |
| Redis/cache | R6: "Redis não usado"; outros: "cache existe" | **Ambos parciais:** `cache.py` é escrito para Redis, mas a dependência não está em `requirements.txt` → cache não-funcional |
| Recomendação "abrir o código" (R1) | Premissa de repo fechado | Improcedente — repo já é público |

**Síntese:** projeto tecnicamente bem estruturado e honestamente documentado, mas com **lacuna entre a promessa ("IA") e a implementação (heurística)** e com **gaps de segurança/compliance graves para fintech**. R6 é a leitura mais confiável; R1 é a menos (operou sem acesso ao código).

---

## 2. Validação dos dados

### ✅ Confirmado (verificado no código)

- **MLMatcher é placeholder:** `src/application/strategies/ml_matcher.py` → `self.model = None  # Placeholder for future ML model loading`; score de pesos fixos `0.40·valor + 0.30·data + 0.20·nsu + 0.10·auth`, teto `min(score, 0.94)`.
- **Bug real de matching:** `_calculate_string_similarity` usa **Jaccard sobre conjunto de caracteres** → `"1234"` vs `"4321"` = **1.0**. NSUs distintos podem casar falsamente.
- **Sem bibliotecas de IA:** nenhum `openai / anthropic / langchain / transformers / ...` em `requirements.txt` nem no código. `.env.example` cita `OPENAI_API_KEY`, `OLLAMA_BASE_URL`, `FREE_MODE_ENABLED`, `CHROMADB_*` — **aspiracionais, não lidos** (só `REDIS_HOST` é lido de fato).
- **RBAC não aplicado:** `require_roles` definido em `src/api/dependencies.py`, **usado em 0 rotas**. Frontend `src/store/auth.store.ts` **fixa o usuário** (`id:'user-123'`, `roles:['user']`, `tenantId:'tenant-123'`) ignorando o JWT → **um único perfil funcional**.
- **Sem trilha de auditoria:** 13 tabelas em `models.py`, nenhuma de auditoria.
- **Sem LGPD em código** (apenas citada em docs); **sem RLS no Postgres** (isolamento só na aplicação); **logout no-op** (sem revogação de `jti`); **sem account lockout**; **sem CSP / Referrer-Policy**; `decode_token_unsafe` existe mas não é usado.
- **Bom de segurança:** bcrypt 12 rounds (+argon2 legado), JWT HS256 (15min/7d, com `jti`), app não sobe sem `SECRET_KEY`, `TenantMiddleware` / `JWTContextMiddleware` presentes.
- **Cache não-funcional:** `src/infrastructure/cache.py` importa `redis.asyncio`, mas `redis` **não está** em `requirements.txt` (falha silenciosa). Rate limiter é in-memory (deques).
- **Worker/scheduler in-process:** `asyncio.create_task` (sem fila externa, **sem recuperação de jobs órfãos** no restart); APScheduler **sem lock distribuído** (multi-instância dispararia em duplicidade).
- **Higiene de repo:** `conciliaai-frontend/src/App.tsxbkp` commitado; **dois lockfiles** (`package-lock.json` + `pnpm-lock.yaml`); `i18next` instalado mas **nunca importado**; `mypy` estrito no `pyproject.toml` mas **advisory no CI** (`mypy src/ || true`).
- **Infra OK:** Dockerfile multistage (Vite+FastAPI, imagem única), compose com Postgres externo + healthcheck, startup roda `alembic upgrade` → `seed_database.py` → uvicorn. Métricas de processo em `/api/v1/reconciliation-jobs/metrics` (p50/p95, throughput, backlog, auto-approval). **Sem** Prometheus/OTEL/Sentry/CD.

### ✅ Confirmado no GitHub (issues reais, abertas, do owner)

- **#99** — 7 testes unitários falhando (parsers Cielo Agiliza/OFX/Rede EDI ×2, import Cielo, reconcile bank statement ×2). Critério: `pytest tests/unit -q` verde (62→69).
- **#100** — CI **não roda no `master`** (branch padrão), pois `ci.yml` dispara só em `main`/`develop`; PR #95 mergeou com **0 checks**. Depende de #99.
- **#96** (reorg `notifications` / `cash_flow`) e **#97** (badge "atualizado há X min") — baixa prioridade.

### ⏳ Pendente / não verificável agora (lacunas a sinalizar)

- **Cobertura real de testes:** desconhecida e **não confiável** enquanto 7 testes falham.
- **UX renderizada:** avaliada só por código; responsividade/PWA/mobile **não executadas**.
- **Comportamento sob carga:** **não há testes de carga** no repo; gargalos são inferidos.
- **Coverage gate:** `pytest.ini` referencia `--cov-fail-under` (issue cita 87), mas o estado efetivo precisa ser confirmado ao reativar o CI.

### ⚠️ Contraditório (entre analistas) — resolvido

RBAC, postura de segurança, acesso ao código e uso de Redis: ver tabela da Seção 1. Em todos, a verdade do código prevalece sobre a opinião do analista.

---

## 3. Plano unificado de ação

Prioridade = impacto × (1 / esforço). Prazos relativos a partir de T0 (data de início da execução).

### 🟥 Fase 0 — Higiene & Verdade (Semana 1) — *quick wins, baixo risco*

| # | Ação | Prazo | Recursos |
|---|---|---|---|
| 0.1 | Corrigir os 7 testes unitários (#99): `FakeAcquirerTransactionRepository` sem `find_chargebacks` / `find_delayed_settlements`; fixture de NSU; asserts de parsers | 2–3 d | — |
| 0.2 | Ativar CI no `master` (#100): add `master` aos triggers do `ci.yml`; confirmar pipeline verde | 0.5 d (após 0.1) | — |
| 0.3 | Higiene: remover `App.tsxbkp`; unificar gerenciador de pacotes (manter **pnpm**, remover `package-lock.json`); declarar `redis` em `requirements.txt` **ou** tornar cache opcional in-memory | 1 d | — |
| 0.4 | **Corrigir bug de similaridade** (Jaccard → `rapidfuzz` Levenshtein/Jaro-Winkler) em `ml_matcher.py` | 1 d | dep `rapidfuzz` |
| 0.5 | Alinhar narrativa de "IA": README/SECURITY honestos; documentar `MLMatcher` como heurístico ponderado | 0.5 d | — |

### 🟧 Fase 1 — Segurança & Compliance crítica (Semanas 2–4) — *destrava venda enterprise*

| # | Ação | Prazo | Recursos |
|---|---|---|---|
| 1.1 | **RBAC real:** aplicar `Depends(require_roles([...]))` nas rotas sensíveis; popular usuário real no front a partir do JWT; criar `GET /users/me` | 1 sem | — |
| 1.2 | **Trilha de auditoria:** tabela `audit_logs` append-only + middleware que registra mutações (actor, tenant, ação, entidade, before/after, ts) | 1 sem | migração Alembic |
| 1.3 | **Hardening:** CSP + Referrer-Policy; account lockout no login; tokens fora do `localStorage`; revogação de refresh (blocklist `jti`); isolar `decode_token_unsafe` | 1 sem | — |
| 1.4 | **LGPD base:** política de retenção; endpoints export/delete por titular; anonimização; (opcional) RLS no Postgres como 2ª barreira | 1–2 sem | apoio jurídico |

### 🟨 Fase 2 — Escala & Observabilidade (Semanas 4–8) — *guiada por métricas*

| # | Ação | Prazo |
|---|---|---|
| 2.1 | Fila/worker externos (**Arq/Celery+Redis** ou Postgres `SKIP LOCKED`) + recuperação de jobs órfãos no startup | 1–2 sem |
| 2.2 | Scheduler distribuído (advisory lock/leader election) + rate limiter e **cache em Redis real** | 1 sem |
| 2.3 | Paginação universal (cursor) + `selectinload` (eliminar N+1) | 1 sem |
| 2.4 | Observabilidade: Prometheus `/metrics` + OpenTelemetry + Sentry + alertas (Slack/email) | 1–2 sem |
| 2.5 | **SSE** para progresso de jobs (substituir polling) | 3–5 d |

### 🟩 Fase 3 — Diferenciação por IA & UX (Semanas 8–16) — *condicionada a dados rotulados*

| # | Ação | Prazo |
|---|---|---|
| 3.1 | **Matcher treinável real** (scikit-learn/LightGBM) sobre histórico de matches aprovados; MLflow; regras como fallback explicável | 3–4 sem |
| 3.2 | **Assistente RAG** sobre `docs/` (FAQ / Text-to-SQL seguro) para usuário não-técnico | 2–3 sem |
| 3.3 | Gaps de frontend: `SettingsPage` real, i18n ativado, a11y (`axe-core`), tela Cielo, onboarding guiado | contínuo |

---

## 4. Sugestões estratégicas

**1. "Verdade em rótulo" + acurácia do matching.**  
Alinhar a narrativa de IA e, no mesmo movimento, corrigir o bug de Jaccard e introduzir ML real de forma faseada.  
*Benefício:* credibilidade do produto + menos falsos positivos/negativos.  
*Risco:* rebranding pode confundir clientes; ML real exige dados rotulados que talvez ainda não existam — **mitigar** começando pela correção determinística e pela coleta de rótulos (matches aprovados) antes de treinar.

**2. Fechar o tripé de compliance fintech (RBAC efetivo + audit log + LGPD) antes de escalar comercialmente.**  
*Benefício:* destrava vendas enterprise, reduz risco regulatório/multas LGPD, atende due diligence.  
*Risco:* esforço alto pode atrasar features — **mitigar** com faseamento (RBAC+auditoria primeiro; LGPD em paralelo com jurídico).

**3. Estabilizar a base como pré-condição de qualquer roadmap.**  
CI verde no `master`, cobertura confiável, segurança no pipeline (`bandit` / `pip-audit`).  
*Benefício:* evita regressões, acelera entregas e habilita crescer o time com segurança.  
*Risco:* praticamente nulo; pequeno custo de oportunidade.

**4. Preparar escala horizontal real guiada por métricas, não prematuramente.**  
*Benefício:* suporta crescimento multi-tenant sem reescrita; remove gargalos in-process (worker, scheduler, rate limiter, cache).  
*Risco:* complexidade/custo de infra se feito cedo — **mitigar** usando o próprio Postgres (`SKIP LOCKED`, advisory locks) antes de adicionar Redis/Celery.

**5. Transformar o motor determinístico (vantagem de auditabilidade) em diferencial.**  
Explicabilidade do match (breakdown dos scores por fator) + assistente RAG sobre a documentação.  
*Benefício:* confiança do auditor, menos suporte/treinamento e entrega o "IA" prometido com baixo risco.  
*Risco:* custo de LLM + alucinação no RAG — **mitigar** com grounding estrito na doc e Text-to-SQL parametrizado/somente-leitura.

---

## 5. Indicadores de sucesso

| Dimensão | Métrica | Alvo |
|---|---|---|
| Estabilidade | Testes verdes / CI no `master` | 69/69 (100%) e CI verde |
| Estabilidade | Cobertura confiável | ≥ 85% (gate ativo) |
| Segurança | Rotas sensíveis com `require_roles` | 100% |
| Segurança | Mutações cobertas por audit log | 100% |
| Segurança | Gaps OWASP fechados (CSP, lockout, token storage, RLS) | 4/4 |
| Compliance | Checklist LGPD (retenção, export, delete, consentimento) | 100% |
| Matching | Precisão/recall (↓ falsos positivos/negativos) | melhora vs. baseline Jaccard |
| Matching | Taxa de auto-approval / MTTR de divergências | ↑ auto-approval, ↓ MTTR |
| Performance | p95 de duração de jobs / latência de API | dentro de SLA |
| Escala | Jobs simultâneos sem duplicação multi-instância | 0 duplicações |
| UX/Adoção | % telas reais (não mock) / score a11y / cliques p/ contestar | 100% reais; a11y sem violações críticas |
| IA (se adotada) | Uplift de acurácia ML vs. heurística / % matches com explicação | uplift mensurável; 100% explicáveis |

---

## 6. Verificação de ponta a ponta

```bash
# Fase 0
pytest tests/unit -q                        # 69/69 passando
pytest tests/integration -m integration    # verde
flake8 src/ tests/                         # limpo
mypy src/                                  # sem regressões

# CI
# Workflow ci.yml deve disparar em push/PR para master → verde

# RBAC (Fase 1)
# Sem papel → 403; com papel → 200
# Frontend exibe usuário/tenant/roles reais do JWT (não mais user-123)

# Audit log (Fase 1)
# Executar mutação (ex.: resolver divergência) →
# registro append-only com actor/tenant/ação/timestamp

# Build
make docker-up                             # imagem única sobe
curl http://localhost:8000/api/v1/health   # 200
pnpm install                               # sem package-lock.json npm
```

---

*Relatório gerado em 2026-06-09 · Executado no branch `claude/epic-gates-nniqsj`*
