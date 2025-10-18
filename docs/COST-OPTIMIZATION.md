# 💸 BuildToValue v7.0 - FinOps & Otimização de Custos

## 🎯 Objetivos
- Controlar o custo de execução das IAs e da infraestrutura.
- Garantir visibilidade por componente e por squad.
- Automatizar ações de redução sem comprometer a qualidade.

## 📈 Princípios
1. **Transparência:** dashboards por ambiente e squad (Grafana + Cloud Billing).
2. **Responsabilidade compartilhada:** FinOps integrado ao ciclo de decisão.
3. **Automação:** políticas de escalonamento e desligamento programadas.

## ⚙️ Estratégias por Camada
- **Aplicação:** use instâncias spot em até 30% do cluster com fallback automático para on-demand.
- **Banco de Dados:** dimensionamento vertical sob demanda + read replicas elásticas.
- **Vector DB:** adicionar shards somente quando índice > 50GB por shard.
- **Cache:** autoscaling por memória (>75%) ou evictions (>100/min).
- **Multi-região:** secundária operando com 50% da capacidade e escalando no failover.

## 🧰 Ferramentas Recomendadas
- **AWS Cost Explorer** + tags `Project`, `Environment`, `Component`.
- **kubecost** para granularidade por namespace/pod.
- **Prometheus** métricas customizadas de custo por decisão.
- **Alertas**: Slack/Teams quando orçamento mensal > 80%.

## 📋 Checklist
- [ ] Tags de custo aplicadas em todos os recursos (Terraform `default_tags`).
- [ ] Orçamentos configurados por ambiente com alertas automáticos.
- [ ] Relatórios semanais revisados pelo squad de FinOps.
- [ ] Ações de desligamento automático fora do horário comercial (ambientes não-prod).
- [ ] Custos de LLM monitorados (`BTOV_FINOPS_BUDGET`).

## 🔗 Referências
- [Deployment Guide](./DEPLOYMENT-GUIDE.md)
- [Performance & Tuning](./PERFORMANCE-TUNING.md)
- [Migration Guide](./MIGRATION-v6-to-v7.md)
