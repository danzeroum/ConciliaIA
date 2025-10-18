# 🌍 BuildToValue v7.0 - Estratégia Multi-Região

## 🎯 Objetivo
Assegurar continuidade de negócio com baixa latência para usuários globais e recuperação rápida em caso de incidentes regionais.

## 🗺️ Arquitetura Geral
```yaml
multi_region_architecture:
  strategy: Active-Passive (auto-failover)
  regions:
    primary:
      name: us-east-1
      azs: 3
      role: Primary traffic
    secondary:
      name: eu-west-1
      azs: 3
      role: Disaster recovery + usuários EU
  disaster_recovery:
    rpo: 15 minutes
    rto: 1 hour
    strategies:
      - Multi-region deployment (active-passive)
      - Automated failover
      - Cross-region DB replication
      - S3 cross-region backup
```

## 💾 Replicação de Dados
- **PostgreSQL:** replicação streaming com failover automático (Patroni ou Aurora Global Database). Meta: lag < 1 segundo.
- **ChromaDB:** snapshots diários + restore automatizado; replicação manual por enquanto.
- **S3:** cross-region replication com tempo máximo de 15 minutos.
- **Redis:** replicação assíncrona ou uso de Redis Enterprise Global Datastore.

## 🌐 Roteamento de Tráfego
```yaml
traffic_routing:
  provider: AWS Route53
  policies:
    - North America -> us-east-1
    - Europe -> eu-west-1
    - Others -> nearest region
  health_checks:
    interval: 30s
    failure_threshold: 3
    automatic_failover: true
    failover_time: < 2 minutes
```

> Utilize `failover` + `geolocation` no Route53. Configure endpoints de saúde (`/actuator/health/ready`) para validação real do serviço.

## 🛠️ Execução de Drills
1. Agende failover trimestral.
2. Execute `terraform apply -var='active_region=eu-west-1'` (ou atualize parâmetros no runbook se usar controle manual).
3. Valide replicação de secrets, bancos e buckets.
4. Rode smoke tests (`./scripts/test-migration.sh --region eu-west-1`).
5. Documente resultados no Decision Ledger.

## 💰 Otimização de Custos
- Dimensione recursos na região secundária com **50% da capacidade** do primário.
- Utilize **spot instances** (50%) com fallback automático para on-demand durante failover.
- Pause workloads não críticos na região secundária quando em standby.

## 📋 Checklist de Conclusão
- [ ] Replicação PostgreSQL monitorada (lag < 1s).
- [ ] Buckets S3 com replication status saudável.
- [ ] Testes de failover executados nos últimos 90 dias.
- [ ] Dashboards (Grafana) integrados às duas regiões.
- [ ] Custos da região secundária revisados mensalmente.

## 📚 Referências Cruzadas
- [Deployment Guide](./DEPLOYMENT-GUIDE.md)
- [Performance & Tuning](./PERFORMANCE-TUNING.md)
- [Security Guide](./SECURITY.md)
