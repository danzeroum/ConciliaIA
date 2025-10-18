# 🚀 BuildToValue v7.0 - Deployment & Infraestruturas

## 📦 Visão Geral de Ambientes

A stack BuildToValue v7 é projetada para operar de forma consistente desde o ambiente local até produção. Utilize os perfis abaixo como base para o seu pipeline de entrega contínua.

```yaml
deployment_modes:
  local_development:
    orchestrator: "Docker Compose"
    components:
      - buildtovalue-app
      - postgres
      - chromadb
      - prometheus
      - grafana
      - jaeger
    startup_time: "< 2 minutes"
    command: "docker-compose -f docker/docker-compose-v7.yml up"

  staging:
    orchestrator: "Docker Swarm | Kubernetes"
    components:
      app:
        replicas: 2
        resources:
          cpu: "1"
          memory: "2Gi"
      postgres:
        replicas: 1
        resources:
          cpu: "2"
          memory: "4Gi"
        persistence: "PVC 50Gi"
      chromadb:
        replicas: 1
        resources:
          cpu: "1"
          memory: "2Gi"
        persistence: "PVC 20Gi"
    monitoring:
      - prometheus
      - grafana
      - jaeger
    ingress: "NGINX Ingress Controller"

  production:
    orchestrator: "Kubernetes"
    architecture: "Multi-AZ for HA"
```

### 💡 Recomendações
- **Homologação** deve ser o mais próxima possível da produção (mesmos manifests, recursos dimensionados).
- Utilize **GitOps (ArgoCD/Flux)** para garantir consistência entre ambientes.
- Configure **pipelines de segurança** (Trivy, Snyk) antes de promover imagens.

## ☁️ Produção em Kubernetes

Abaixo um resumo da configuração recomendada para produção.

```yaml
components:
  app:
    deployment:
      replicas: 3
      strategy: RollingUpdate
      maxUnavailable: 1
      maxSurge: 1
    resources:
      requests: { cpu: "2", memory: "4Gi" }
      limits:   { cpu: "4", memory: "8Gi" }
    autoscaling:
      enabled: true
      minReplicas: 3
      maxReplicas: 10
      targetCPU: 70
      targetMemory: 80
    health_checks:
      liveness: "/actuator/health/liveness"
      readiness: "/actuator/health/readiness"
      startup: "/actuator/health/startup"

  postgres:
    deployment: StatefulSet
    replicas: 3  # 1 primary + 2 read replicas
    resources:
      requests: { cpu: "4", memory: "16Gi" }
      limits:   { cpu: "8", memory: "32Gi" }
    persistence:
      storageClass: "ssd"
      size: "500Gi"
    backup:
      schedule: "0 2 * * *"
      retention: "30 days"
      destination: "S3/GCS"

  chromadb:
    deployment: StatefulSet
    replicas: 2
    persistence:
      storageClass: "ssd"
      size: "200Gi"

  redis:
    deployment: StatefulSet
    mode: Cluster
    replicas: 6  # 3 masters + 3 replicas

  prometheus:
    deployment: StatefulSet
    retention: 30d
    persistence: { size: "100Gi" }

  grafana:
    deployment: Deployment
    replicas: 2
    persistence: { size: "10Gi" }

  jaeger:
    deployment: "All-in-one (small) | Production (large)"
    components:
      collector: { replicas: 3 }
      query:     { replicas: 2 }
      storage:   "Elasticsearch | Cassandra"
```

### 🔐 Networking & Segurança
- **Ingress Controller:** NGINX com TLS via Cert-Manager + Let's Encrypt.
- **Network Policies:**
  - app pode acessar postgres, chromadb e redis.
  - prometheus pode coletar métricas de todos os pods.
  - negar todo tráfego restante.
- **Pod Security Standards:** `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation=false`.
- **Secrets:** utilize Sealed Secrets ou External Secrets Operator com rotação automática a cada 90 dias.

## 🛠️ Infrastructure as Code (Terraform)

O exemplo a seguir demonstra como provisionar a base AWS (VPC, EKS, RDS, Redis e buckets de backup) utilizando Terraform 1.5+.

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.5"
  backend "s3" {
    bucket = "buildtovalue-terraform-state"
    key    = "v7/production/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-lock"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "BuildToValue"
      Version     = "7.0"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source = "./modules/vpc"
  name               = "buildtovalue-${var.environment}"
  cidr               = var.vpc_cidr
  availability_zones = var.azs
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  enable_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}
```

> Consulte o arquivo completo para definição dos módulos `eks`, `rds`, `redis` e recursos S3/CloudWatch. Utilize **Terraform Cloud** ou **remote backend** para state locking e times colaborativos.

### 📌 Boas Práticas
- Separe workspaces por ambiente (`dev`, `staging`, `prod`).
- Habilite **Cost Allocation Tags** e dashboards FinOps.
- Utilize **terraform-docs** para manter variáveis e outputs documentados.

## 🐳 Manifests Kubernetes

O manifesto padrão (`k8s/production/app-deployment.yaml`) cobre deployment, service e HPA com probes configuradas.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: buildtovalue-app
  namespace: buildtovalue
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      serviceAccountName: buildtovalue-app
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      initContainers:
        - name: wait-for-postgres
          image: busybox:1.35
          command: ['sh','-c','until nc -z postgres-service 5432; do echo waiting; sleep 2; done']
      containers:
        - name: app
          image: buildtovalue/app:v7.0.0
          ports:
            - { name: http,        containerPort: 8080 }
            - { name: management,  containerPort: 9090 }
          env:
            - { name: SPRING_PROFILES_ACTIVE, value: "production" }
            - { name: POSTGRES_HOST, value: "postgres-service" }
            - { name: POSTGRES_DB,   value: "buildtovalue" }
            - name: POSTGRES_USER
              valueFrom: { secretKeyRef: { name: postgres-credentials, key: username } }
            - name: POSTGRES_PASSWORD
              valueFrom: { secretKeyRef: { name: postgres-credentials, key: password } }
            - { name: REDIS_HOST, value: "redis-service" }
          resources:
            requests: { cpu: "2", memory: "4Gi" }
            limits:   { cpu: "4", memory: "8Gi" }
          livenessProbe:
            httpGet: { path: /actuator/health/liveness, port: management }
            initialDelaySeconds: 60
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /actuator/health/readiness, port: management }
            initialDelaySeconds: 30
            periodSeconds: 5
          startupProbe:
            httpGet: { path: /actuator/health/startup, port: management }
            periodSeconds: 10
            failureThreshold: 30
          volumeMounts:
            - { name: config,            mountPath: /app/config,          readOnly: true }
            - { name: buildtovalue-data, mountPath: /app/.buildtovalue }
      volumes:
        - name: config
          configMap: { name: buildtovalue-config }
        - name: buildtovalue-data
          persistentVolumeClaim: { claimName: buildtovalue-pvc }
```

> Configure secrets com **External Secrets Operator** quando disponível. Sempre valide manifests com `kubeval` e `konftest` durante o CI.

## 📈 Escalabilidade

Escalonar horizontalmente é a estratégia primária para lidar com o aumento de decisões processadas.

```yaml
scaling_strategy:
  application_tier:
    method: Horizontal Pod Autoscaling (HPA)
    triggers:
      cpu:
        threshold: 70%
        action: "Scale up by 50% or 2 pods (whichever is greater)"
      memory:
        threshold: 80%
        action: "Scale up by 50% or 2 pods"
      custom_metrics:
        - metric: decisions_per_second
          threshold: 10
          action: Scale up
        - metric: avg_decision_duration
          threshold: 5s
          action: Scale up
    limits:
      min_replicas: 3
      max_replicas: 10
      cooldown_period: 5 minutes
    cost_optimization:
      use_spot_instances: true
      spot_percentage: 30
      fallback_to_on_demand: true

  database_tier:
    method: Vertical + Read Replicas
    vertical_scaling:
      triggers:
        - CPU > 80% for 10 minutes
        - Memory > 85% for 10 minutes
        - Connection pool exhaustion
      actions:
        - Increase instance size
        - Add read replicas
        - Enable connection pooling
    read_replicas:
      min: 1
      max: 5
      auto_scale: true
      lag_threshold: 100ms
```

### 📌 Notas Operacionais
- Utilize **KEDA** para métricas customizadas (decisions_per_second, backlog de filas).
- Configure **PGBouncer** para pooling de conexões PostgreSQL.
- Para Redis Cluster, monitore evictions e latência para definir novos shards.

## 🌍 Distribuição Geográfica

A arquitetura de DR usa estratégia **Active-Passive** com failover automático e replicação contínua.

```yaml
multi_region_architecture:
  strategy: Active-Passive (with auto-failover)
  regions:
    primary:
      region: us-east-1
      availability_zones: 3
      purpose: Primary traffic
    secondary:
      region: eu-west-1
      availability_zones: 3
      purpose: DR + geo-distributed users
  data_replication:
    postgres:
      method: Streaming replication
      lag_target: < 1 second
      failover: Automatic
    s3:
      method: Cross-region replication
      replication_time: < 15 minutes
    vector_db:
      method: Manual snapshot + restore
      frequency: Daily
      rto: < 4 hours
  traffic_routing:
    method: Route53 Geolocation + Health Checks
    failover:
      health_check_interval: 30s
      failure_threshold: 3
      automatic_failover: true
      failover_time: < 2 minutes
  cost_optimization:
    secondary_region:
      instance_size: 50% of primary
      scale_up_on_failover: true
      spot_instances: 50%
```

> Execute **drills trimestrais** para validar RPO (15 minutos) e RTO (1 hora). Automatize replicação de secrets e backups S3 cross-region.

## 📚 Referências Cruzadas
- [Arquitetura Geral](./ARCHITECTURE.md)
- [Guia de Orquestração](./ORCHESTRATION-GUIDE.md)
- [Guia de Observabilidade](./TROUBLESHOOTING.md)
- [FinOps & Custos](./COST-OPTIMIZATION.md)
