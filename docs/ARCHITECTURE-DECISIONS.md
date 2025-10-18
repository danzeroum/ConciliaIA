# 📘 BuildToValue v7.0 - Architecture Decision Log (ADR)

## ADR-ARCH-001: Clean Architecture + Hexagonal Architecture
- **Data:** 2025-01-15
- **Status:** Aceito
- **Contexto:** Necessidade de separação clara de responsabilidades na orquestração complexa.
- **Decisão:** Adotar Clean Architecture com Ports & Adapters.
- **Consequências:**
  - ✅ Alta testabilidade e independência de frameworks.
  - ✅ Facilidade de troca de provedores LLM.
  - ⚠️ Mais boilerplate e curva de aprendizado.

## ADR-ARCH-002: Arquitetura Orientada a Eventos para Inter-IA
- **Data:** 2025-01-20
- **Status:** Aceito
- **Contexto:** Comunicação assíncrona entre IAs sem acoplamento forte.
- **Decisão:** Utilizar Kafka/RabbitMQ para eventos inter-IA.
- **Consequências:**
  - ✅ Baixo acoplamento e escalabilidade.
  - ✅ Trilhas de auditoria nativas.
  - ⚠️ Consistência eventual e debugging mais complexo.

## ADR-ARCH-003: Ledger Imutável de Decisões
- **Data:** 2025-01-22
- **Status:** Aceito
- **Contexto:** Necessidade de rastreabilidade completa.
- **Decisão:** Ledger append-only em JSONL com backup opcional em blockchain.
- **Consequências:**
  - ✅ Auditoria completa.
  - ✅ Fácil análise posterior.
  - ⚠️ Crescimento de storage (mitigado por arquivamento).

## ADR-ARCH-004: PostgreSQL como Banco Primário
- **Data:** 2025-01-25
- **Status:** Aceito
- **Contexto:** Banco ACID com suporte a JSON e escala vertical.
- **Decisão:** PostgreSQL 15+ como datastore primário.
- **Consequências:**
  - ✅ Maturidade e consistência forte.
  - ✅ Excelente suporte a JSON.
  - ⚠️ Necessidade de sharding futuro para cargas extremas.

## ADR-ARCH-005: ChromaDB para Vetores
- **Data:** 2025-01-28
- **Status:** Aceito
- **Contexto:** Busca semântica eficiente para Auto-RAG.
- **Decisão:** Adotar ChromaDB para embeddings.
- **Consequências:**
  - ✅ Integração simples com Python.
  - ✅ Performance para < 1M vetores.
  - ⚠️ Limitado a nó único por enquanto.

## ADR-ARCH-006: Kubernetes em Produção
- **Data:** 2025-02-01
- **Status:** Aceito
- **Contexto:** Necessidade de orquestração robusta.
- **Decisão:** Kubernetes como plataforma padrão de produção.
- **Consequências:**
  - ✅ Padrão de mercado e ecossistema sólido.
  - ✅ Auto-escalonamento nativo.
  - ⚠️ Complexidade operacional elevada.

## Próximos Candidatos
- **ADR-ARCH-007:** Service Mesh opcional (Istio/Linkerd) para mTLS.
- **ADR-ARCH-008:** Federated Learning para squads multi-tenant.

> Todas as decisões devem ser registradas também no Decision Ledger para rastreabilidade histórica.
