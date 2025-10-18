## ⚡ Quick Start (3 Commands)

```bash
# 1. Clone repository
git clone https://github.com/your-username/buildtovalue-v7.git
cd buildtovalue-v7

# 2. Copy environment file and add your API keys
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY and other keys

# 3. Run complete setup
./scripts/setup-complete.sh

# That's it! 🎉
```

### First Decision

```bash
# Route your first problem
./scripts/orchestrator/route-problem.sh "Create a simple todo list app"

# Check result
./scripts/ledger/show-last-decision.sh
```

# 🚀 BuildToValue v7.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-7.0.0-blue.svg)](https://github.com/buildtovalue/v7/releases)
[![Certification](https://img.shields.io/badge/certified-Gold-gold.svg)](./docs/CERTIFICATION-GUIDE.md)

> **"De Squad sobre Solo vem Sinergia. De Sinergia vem Velocidade. De Velocidade vem Valor."**

## 📎 O que é BuildToValue v7?

**BuildToValue v7** é uma metodologia de desenvolvimento Full-Stack orientada por **IA Squad Cooperativa**, transformando desenvolvimento de software em um ecossistema adaptativo e inteligente.

### 🎯 Diferenciais v7

- **🤖 Squad Expandida**: 11 personas especializadas com mental models baseados em referências consagradas
- **🧠 Orquestração Inteligente**: Roteamento automático contextual com aprendizado contínuo
- **⚖️ Autonomia Progressiva**: Sistema de confiança que evolui de 1 (supervisão total) a 5 (autonomia completa)
- **📚 Auto-RAG**: Indexação automática de lições aprendidas e padrões de sucesso
- **🔄 Comunicação Inter-IAs**: Protocolos formais de consultation, alert e suggestion
- **📊 Observabilidade Total**: Dashboards técnicos + negócio + saúde da squad
- **🛡️ Ethics & Safety**: Guardrails éticos e de segurança integrados
- **💰 FinOps Integration**: Otimização automática de custos de IA/infra

### ⚡ Evolução v6 → v7

| Aspecto | v6 | v7 |
|---------|----|----|
| Personas | 5 básicas | 11 especializadas |
| Mental Models | Implícitos | Explícitos com referências |
| Orquestração | Manual | Automática + ML |
| Autonomia | Fixa | Progressiva (níveis 1-5) |
| Aprendizado | Nenhum | Auto-RAG + Lessons Learned |
| Comunicação | Handoffs formais | Inter-IA + Handoffs |
| Ética | Ad-hoc | Guardian dedicado |
| Custos | Não rastreado | FinOps integrado |
| Conflitos | Reativo | Preditivo |

## 🏗️ Arquitetura
```
┌─────────────────────────────────────────────────────────┐
│                  Prompt Engineer                         │
│              (Estratégia & Supervisão)                   │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │  Smart Orchestrator  │
          │  (Roteamento + ML)   │
          └──────────┬───────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│ Strategy  │ │  Design   │ │ Technical │
│  Squad    │ │   Squad   │ │   Squad   │
├───────────┤ ├───────────┤ ├───────────┤
│ Product   │ │ Designer  │ │ Arquiteto │
│ Manager   │ │           │ │           │
│           │ │           │ │ Developer │
│ Business  │ │           │ │           │
│ Analyst   │ │           │ │ QA        │
│           │ │           │ │           │
│           │ │           │ │ Auditor   │
└───────────┘ └───────────┘ └───────────┘

┌─────────────────────────────────────┐
│         Support Squad               │
├─────────────────────────────────────┤
│ Ops │ Data Arch │ Integration │ Ethics │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Pré-requisitos
```bash
# Mínimos
- Git 2.30+
- Docker 20.10+
- Python 3.11+ OU Java 17+ (conforme stack escolhida)
- 8GB RAM disponível
- 20GB disco livre

# APIs necessárias (pelo menos uma)
- OpenAI API Key (GPT-4)
- Anthropic API Key (Claude)
- Google AI API Key (Gemini)
```

### Instalação Nova (< 3 minutos)
```bash
# 1. Clone o template v7
git clone https://github.com/buildtovalue/template-v7.git my-project
cd my-project

# 2. Inicialização interativa
./scripts/init-v7.sh
# Prompts:
# - Project name: [my-awesome-product]
# - Domain: [fintech/healthtech/saas/ecommerce]
# - Target buyer: [startup/enterprise]
# - Foundation level: [lite/standard/enterprise]
# - Primary language: [java/python/node/polyglot]

# 3. Configurar variáveis
cp .env.example .env.dev
nano .env.dev
# Adicionar: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

# 4. Primeira execução
./scripts/gates-v7.sh --setup  # Valida instalação
docker-compose -f docker/docker-compose-v7.yml up -d
./scripts/start-app.sh

# 5. Acessar dashboards
open http://localhost:8080        # Aplicação
open http://localhost:3000        # Grafana (admin/admin)
open http://localhost:9090        # Prometheus
open http://localhost:16686       # Jaeger (tracing)
```

### Migração v6 → v7 (< 10 minutos)
```bash
# 1. Backup completo
./scripts/backup-project.sh

# 2. Executar migração automática
./scripts/migrate-v6-to-v7.sh
# O script:
# - Converte .buildtoflip → .buildtovalue
# - Migra consensus files
# - Cria personas com mental models
# - Configura orchestration
# - Setup observabilidade

# 3. Validar migração
./scripts/gates-v7.sh --migration-check

# 4. Review manual
# - Customizar personas em .buildtovalue/squad/personas/
# - Ajustar activation matrix para seu contexto
# - Revisar mental models references

# 5. Primeira execução v7
./scripts/start-app.sh
```

## 🤖 Squad de IAs v7

### Personas Disponíveis

| Persona | Responsabilidade | Mental Model Primário | Autonomia |
|---------|------------------|----------------------|-----------|
| **IA-Product-Manager** | Visão estratégica | "Inspired" (Marty Cagan) | L3 |
| **IA-Business-Analyst** | Regras de negócio | "User Story Mapping" (Patton) | L3 |
| **IA-Arquiteto** | Decisões técnicas | "Clean Architecture" + DDD | L4 |
| **IA-Developer** | Implementação | "Clean Code" + Pragmatic Prog | L3 |
| **IA-QA-Engineer** | Qualidade | "Lessons Learned Testing" | L3 |
| **IA-Auditor** | Segurança | "Web App Hacker's Handbook" | L5 |
| **IA-Designer** | UX/UI | "Don't Make Me Think" | L3 |
| **IA-Ops** | Infra/DevOps | "Phoenix Project" + SRE | L4 |
| **IA-Data-Architect** | Governança dados | DAMA-DMBOK | L3 |
| **IA-Integration-Specialist** | Cross-platform | "Enterprise Integration Patterns" | L4 |
| **IA-Ethics-Guardian** | Ética e viés | "Weapons of Math Destruction" | L5 |

**Níveis de Autonomia:**
- **L1**: Apenas sugere, humano aprova tudo
- **L2**: Executa tasks simples, notifica humano
- **L3**: Autonomia moderada, humano revisa periodicamente
- **L4**: Alta autonomia, intervenção apenas em exceções
- **L5**: Autonomia total, pode vetar decisões de outras IAs

### Ativação Automática
```bash
# Roteamento inteligente baseado em contexto
./scripts/orchestrator/route-problem.sh "Implementar autenticação OAuth2"

# Output:
# 🎯 Análise de Problema:
#   Tipo: security_implementation
#   Complexidade: high
#   Impacto: critical
#
# 🤖 Squad Recomendada:
#   Primary: IA-Auditor (confidence: 0.92)
#   Support: IA-Arquiteto (0.85), IA-Developer (0.78)
#
# 📋 Sequência Sugerida:
#   1. IA-Auditor → Define requisitos segurança OAuth2
#   2. IA-Arquiteto → Projeta arquitetura auth flow
#   3. IA-Developer → Implementa com validação contínua
#   4. IA-QA → Testes segurança + penetration
#   5. IA-Ops → Deploy com monitoring
#
# ⚡ Executar agora? [Y/n]
```

## 📚 Comandos Essenciais

### Orquestração
```bash
# Ativar IA específica com contexto
./scripts/orchestrator/activate-ia.sh ia-arquiteto \
  --context="performance_optimization" \
  --urgency="high"

# Handoff formal entre IAs
./scripts/orchestrator/handoff.sh \
  --from=ia-arquiteto \
  --to=ia-developer \
  --artifacts="ADR-005,component-diagram.svg"

# Resolver conflito entre IAs
./scripts/orchestrator/resolve-conflict.sh \
  --ias="ia-arquiteto,ia-developer,ia-auditor" \
  --topic="database_choice" \
  --method="weighted_voting"
```

### Aprendizado
```bash
# Capturar lição aprendida
./scripts/learning/capture-lesson.sh \
  --trigger="incident" \
  --category="performance" \
  --severity="high" \
  --description="Query N+1 causou timeout"

# Construir índice RAG
./scripts/learning/build-rag-index.sh --incremental

# Executar experimento A/B
./scripts/learning/run-experiment.sh \
  --name="routing-strategy-v2" \
  --variants="historical,semantic" \
  --sample-size=100
```

### Quality Gates
```bash
# Todos os gates (completo)
./scripts/gates-v7.sh --full

# Apenas gates de squad
./scripts/gates-v7.sh --squad

# Apenas gates de negócio
./scripts/gates-v7.sh --business

# Gates com relatório detalhado
./scripts/gates-v7.sh --full --report=json > gates-report.json
```

### Monitoramento
```bash
# Verificar saúde da squad
./scripts/monitoring/check-squad-health.sh

# Rastrear decisão específica
./scripts/monitoring/trace-decision.sh --id="DEC-2025-001"

# Exportar métricas período
./scripts/monitoring/export-metrics.sh \
  --format="json" \
  --period="last-sprint" \
  --output="metrics-sprint-15.json"

# Analisar custos FinOps
./scripts/monitoring/finops-report.sh --period="last-month"
```

## 📊 Quality Gates v7

### Gates Técnicos

| Gate | Critério MVP | Critério Production | Comando |
|------|--------------|---------------------|---------|
| Cobertura Testes | ≥ 60% | ≥ 80% | `./scripts/gates/test-coverage.sh` |
| Performance P95 | < 800ms | < 500ms | `./scripts/gates/performance.sh` |
| Vulnerabilidades | Critical: 0 | All: 0 | `./scripts/gates/security-scan.sh` |
| Lighthouse | ≥ 80 | ≥ 90 | `./scripts/gates/lighthouse.sh` |
| Healthcheck | Básico | Detalhado | `./scripts/gates/health.sh` |

### Gates de Squad (Novos v7)

| Gate | Target | Comando |
|------|--------|---------|
| Tempo Handoff | < 10 min | `./scripts/gates/handoff-time.sh` |
| Confidence Média | > 0.75 | `./scripts/gates/confidence.sh` |
| Taxa Conflitos | < 5% | `./scripts/gates/conflicts.sh` |
| Saúde Individual | > 4/5 | `./scripts/gates/ia-health.sh` |
| Comunicação Inter-IA | > 80% efetividade | `./scripts/gates/inter-ia-comm.sh` |

### Gates de Negócio (Novos v7)

| Métrica | Target | Fonte |
|---------|--------|-------|
| Lead Time Feature | < 5 dias | Ledger |
| Deployment Frequency | ≥ 2x/semana | Pipeline |
| MTTR | < 1 hora | Incidents |
| Change Failure Rate | < 5% | Deploys |
| Customer NPS | > 50 | Feedback |

### Gates de Ethics & FinOps (Novos v7)

| Gate | Target | Comando |
|------|--------|---------|
| Bias Detection | 0 high-risk | `./scripts/gates/ethics-bias.sh` |
| Custo por Decisão | < $0.05 | `./scripts/gates/finops-cost.sh` |
| Carbon Footprint | Trend ↓ | `./scripts/gates/sustainability.sh` (v7.1) |

## 🎓 Certificação
```bash
# Verificar status de certificação
./scripts/certification/check-status.sh

# Gerar relatório completo
./scripts/certification/generate-report.sh

# Submeter para certificação
./scripts/certification/submit.sh --level=silver
```

### Níveis

- **🥉 Bronze**: Squad básica + gates 80% + 10 decisões no ledger (Validade: 6 meses)
- **🥈 Prata**: Squad completa + Auto-RAG + 50 casos + observabilidade (Validade: 12 meses)
- **🥇 Ouro**: Aprendizado contínuo + tracing + auto-healing + contribuição (Vitalício)

## 📖 Documentação Completa

- **[Guia de Arquitetura](./docs/ARCHITECTURE.md)** - Detalhes técnicos completos
- **[Especificação de Personas](./docs/SQUAD-PERSONAS.md)** - Cada IA em detalhes
- **[Guia de Orquestração](./docs/ORCHESTRATION-GUIDE.md)** - Como gerenciar a squad
- **[Migração v6→v7](./docs/MIGRATION-v6-to-v7.md)** - Passo a passo detalhado
- **[Referência de Scripts](./docs/SCRIPTS-REFERENCE.md)** - Todos os comandos
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Resolução de problemas
- **[Deployment & Infra](./docs/DEPLOYMENT-GUIDE.md)** - Ambientes, IaC e multi-região
- **[Segurança](./docs/SECURITY.md)** - Hardening e playbooks de resposta
- **[Performance & Tuning](./docs/PERFORMANCE-TUNING.md)** - Estratégias, benchmarks e testes de carga
- **[FinOps & Custos](./docs/COST-OPTIMIZATION.md)** - Governança de custos
- **[Guia de Desenvolvimento](./docs/DEVELOPMENT-GUIDE.md)** - Fluxo diário e padrões de código
- **[Onboarding](./docs/ONBOARDING.md)** - Trilha para novos integrantes
- **[Stack Tecnológica](./docs/TECHNOLOGY-STACK.md)** - Ferramentas adotadas
- **[ADR Log](./docs/ARCHITECTURE-DECISIONS.md)** - Decisões arquiteturais
- **[Estrutura de Documentação](./docs/DOCUMENTATION-STRUCTURE.md)** - Matriz de artefatos

## 🗺️ Roadmap

### v7.1 (Q2 2025)
- Multi-linguagem support (Polyglot)
- Sustainability metrics (Carbon)
- Zero-touch onboarding
- Comunidade contributions gate

### v7.2 (Q3 2025)
- Natural language orchestration
- Auto-optimization ML
- Sentiment analysis handoffs
- Proactive suggestions

### v8.0 (2026)
- Industry-specific templates
- Marketplace de personas
- Federated squads
- Self-healing architecture completo

## 🤝 Contribuindo
```bash
# 1. Fork o repositório
# 2. Crie branch feature
git checkout -b feature/amazing-improvement

# 3. Commit com padrão
git commit -m "feat(squad): adiciona IA-DataScientist persona"

# 4. Push e PR
git push origin feature/amazing-improvement

# 5. Aguarde review da squad ;)
```

## 📞 Suporte

- **Docs**: [docs.buildtovalue.com](https://docs.buildtovalue.com)
- **Discord**: [discord.gg/buildtovalue](https://discord.gg/buildtovalue)
- **GitHub Issues**: [github.com/buildtovalue/v7/issues](https://github.com/buildtovalue/v7/issues)
- **Email**: support@buildtovalue.com

## 📄 Licença

MIT License - Veja [LICENSE](./LICENSE) para detalhes.

---

© 2025 BuildToValue v7 | **"Squad sobre Solo, Valor sobre Complexidade"**
