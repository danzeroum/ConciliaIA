# 🛠️ BuildToValue v7.0 - Guia de Desenvolvimento

## ✅ Pré-requisitos
Execute `./scripts/check-prerequisites.sh` para validar:
- Docker 20.10+
- Python 3.11+
- Java 17+ (para backend Java)
- Git 2.30+
- 8GB RAM livre, 20GB disco

## ⚡ Setup Rápido
```bash
git clone https://github.com/buildtovalue/template-v7.git my-project
cd my-project
./scripts/dev-setup.sh
```
O script instala dependências, gera `.env.dev`, sobe serviços em Docker e roda gates iniciais.

## 🧪 Workflow Diário
- `./scripts/dev-start.sh` → inicia serviços
- `./scripts/dev-stop.sh`  → encerra
- `./scripts/dev-logs.sh`  → acompanha logs
- `./scripts/dev-shell.sh` → shell do container app

### Hot Reload
- Java: `./mvnw spring-boot:run -Dspring-boot.run.profiles=dev`
- Python: `python -m uvicorn orchestrator.main:app --reload`

### Testes
- `./scripts/test-all.sh`
- `./scripts/test-unit.sh`
- `./scripts/test-integration.sh`
- `./scripts/test-e2e.sh`

### Quality Gate antes do commit
`./scripts/pre-commit-check.sh` (lint, testes, security scan, licença)

## 🧱 Organização de Código
```yaml
code_organization:
  backend_java:
    package_structure: |
      com.buildtovalue.{project}
        adapter/
          in/web        # Controllers
          out/persistence # JPA repositories
        core/
          domain/      # Entidades
          port/        # Interfaces (ports)
          service/     # Casos de uso
        config/        # Configurações Spring
        exception/     # Handlers
    naming_conventions:
      controllers: {Entity}Controller
      services: {UseCase}Service
      repositories: {Entity}Repository
      dtos: {Entity}DTO
    testing:
      unit_tests: src/test/java/.../unit
      integration_tests: src/test/java/.../integration
      naming: {Method}_{Scenario}_{Expected}

  orchestrator_python:
    module_structure: |
      orchestrator/
        agents/
        core/
          routing.py
          consensus.py
          confidence.py
        learning/
          rag.py
          lessons.py
        monitoring/
          tracing.py
          metrics.py
        utils/
    naming_conventions:
      classes: PascalCase
      functions: snake_case
      constants: UPPER_SNAKE_CASE
    type_hints: Required for public functions
    docstrings: Google style

  configuration:
    env_prefix: BTV_
    preferred_format: YAML
    secret_policy: Nunca versionar secrets; usar Vault/Secrets Manager
```

## 🌳 Fluxo de Git
```yaml
git_workflow:
  branching:
    model: GitFlow adaptado
    main: production-ready
    develop: integração contínua
    feature/*: features (ex: feature/BTV-123-add-ethics-guardian)
    bugfix/*: correções
    hotfix/*: emergências (merge em main + develop)
  commits:
    convention: Conventional Commits
    exemplos:
      - feat(squad): add IA-Ethics-Guardian persona
      - fix(routing): correct confidence calculation
      - docs(architecture): update deployment section
```

## 📋 Checklist Antes do PR
- [ ] Código segue padrões de estilo.
- [ ] Self-review completo.
- [ ] Comentários adicionados para lógica complexa.
- [ ] Documentação atualizada.
- [ ] Sem breaking changes (ou devidamente comunicados).
- [ ] Todos os quality gates aprovados.

## 📚 Referências
- [Checklist de Implementação](./IMPLEMENTATION-CHECKLIST.md)
- [Orchestration Guide](./ORCHESTRATION-GUIDE.md)
- [Technology Stack](./TECHNOLOGY-STACK.md)
