# 🎓 BuildToValue v7.0 - Certification Guide

## 🧭 Objetivo
Orientar squads na obtenção das certificações oficiais BuildToValue (Bronze, Prata, Ouro) garantindo conformidade técnica, ética e de valor entregue.

## 🏅 Níveis de Certificação
| Nível | Requisitos Principais | Validade |
|-------|-----------------------|----------|
| Bronze | Squad básica, quality gates ≥ 80%, 10 decisões registradas | 6 meses |
| Prata | Squad completa, Auto-RAG ativo, 50 casos catalogados, observabilidade total | 12 meses |
| Ouro | Aprendizado contínuo, tracing fim-a-fim, auto-healing, contribuição para comunidade | Vitalício |

## 🧩 Estrutura do Programa
1. **Avaliação Inicial:** diagnóstico do estado atual (scripts de health check).
2. **Plano de Ação:** definição de gaps e roadmap de melhoria.
3. **Evidências:** coleta de artefatos, métricas e decisões.
4. **Auditoria:** revisão por comitê BuildToValue.
5. **Certificação:** emissão de certificado digital + badge.

## 📋 Checklist por Nível
### Bronze
- [ ] Personas essenciais configuradas (PM, BA, Developer, QA, Auditor)
- [ ] Activation matrix funcional (confiança média ≥ 0.65)
- [ ] Decision Ledger com pelo menos 10 entradas completas
- [ ] Quality gates técnicos executados semanalmente
- [ ] Ethics Guardian sem bloqueios críticos pendentes

### Prata
- [ ] Todas as personas v7 habilitadas e com mental models documentados
- [ ] Auto-RAG com índice atualizado (`build-rag-index.sh`)
- [ ] Observabilidade integrada (Prometheus, Grafana, Jaeger)
- [ ] FinOps ativo com relatórios mensais
- [ ] 50 decisões registradas com outcomes avaliados
- [ ] Processos de handoff com tempo médio < 10 minutos

### Ouro
- [ ] Autonomia média ≥ L4 sem incidentes críticos
- [ ] Confiança média ≥ 0.8 e tendência positiva
- [ ] Tracing completo (`problem.route` → `ia.execute` → `handoff`)
- [ ] Processos de auto-healing configurados
- [ ] Contribuição aberta (templates, mental models, scripts)
- [ ] Auditoria ética trimestral com zero blockers

## 🛠️ Scripts de Suporte
| Fase | Script | Finalidade |
|------|--------|------------|
| Avaliação | `./scripts/certification/check-status.sh` | Mostra progresso atual por nível |
| Evidências | `./scripts/certification/generate-report.sh --format pdf` | Gera dossiê com métricas e artefatos |
| Submissão | `./scripts/certification/submit.sh --level prata` | Envia documentação para o comitê |
| Auditoria | `./scripts/ledger/generate-adr.sh` | Referencia decisões críticas |
| Pós-certificação | `./scripts/certification/renew.sh --level bronze` | Inicia processo de renovação |

## 📄 Evidências Necessárias
- **Decision Ledger:** IDs, resultados, métricas de confiança e custo
- **Dashboards:** screenshots ou exports de métricas principais
- **Runbooks:** planos de contingência e respostas a incidentes
- **Políticas Éticas:** registros de revisões do Ethics Guardian
- **Contribuições:** links para PRs ou pacotes compartilhados

## 🕒 Linha do Tempo Recomendada
| Semana | Atividade |
|--------|-----------|
| 1 | Avaliação inicial + plano de ação |
| 2-4 | Implementar melhorias prioritárias |
| 5 | Revisão de métricas + ajustes finais |
| 6 | Geração de relatório e submissão |
| 7 | Auditoria oficial |
| 8 | Recebimento de certificado |

## 🔄 Renovação
- Bronze/Prata: iniciar processo 30 dias antes da expiração.
- Ouro: revisão anual opcional para manter badge ativo na comunidade.
- Use `./scripts/certification/renew.sh --level <nivel>` para automatizar.

## 📬 Contato com Comitê
- Email: danniellau@gmail.com
- Discord: `#btv-certification`
- SLA de resposta: até 5 dias úteis

---
> **Nota:** Certificação Ouro exige auditoria externa e entrevistas com stakeholders humanos.
