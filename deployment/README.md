# ConciliaAI - Deployment Guide

## Prerequisites

- AWS CLI configured with credentials
- Terraform >= 1.5
- Docker >= 20.10
- PostgreSQL client (psql)
- Python >= 3.11

## Quick Deploy - Phase 1 Alpha

```bash
# 1. Set environment variables
export AWS_PROFILE=conciliaai-prod
export AWS_REGION=us-east-1

# 2. Run deployment script
./scripts/deploy-phase1-alpha.sh

# 3. Verify deployment
curl https://your-alb-dns.us-east-1.elb.amazonaws.com/health
```

## Manual Deployment Steps

### 1. Build Docker Image

```bash
docker build -t conciliaai-api:latest -f Dockerfile .
```

### 2. Push to ECR

```bash
# Login
aws ecr get-login-password --region us-east-1 | \
docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag conciliaai-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/conciliaai-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/conciliaai-api:latest
```

### 3. Deploy Infrastructure

```bash
cd infrastructure/terraform

terraform init
terraform plan -var="environment=alpha" -out=tfplan
terraform apply tfplan
```

### 4. Run Migrations

```bash
cd migrations

PGPASSWORD=<password> psql \
  -h <rds-endpoint> \
  -U conciliaai_admin \
  -d conciliaai \
  -f 001_initial_schema.sql
```

### 5. Deploy Application

```bash
aws ecs update-service \
  --cluster conciliaai-alpha \
  --service conciliaai-api \
  --force-new-deployment
```

## Environment Variables

```bash
# Application
ENVIRONMENT=alpha
LOG_LEVEL=INFO
DEBUG=false

# Database
DB_HOST=<rds-endpoint>
DB_PORT=5432
DB_NAME=conciliaai
DB_USER=conciliaai_admin
DB_PASSWORD=<password>

# Redis
REDIS_HOST=<redis-endpoint>
REDIS_PORT=6379
REDIS_PASSWORD=<password>

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=<account>

# Security
SECRET_KEY=<secret>
JWT_SECRET=<jwt-secret>
```

## Monitoring

### CloudWatch Dashboards

- **API Metrics**: ECS CPU/Memory, Request latency
- **Database**: RDS connections, query performance
- **Business KPIs**: Matching accuracy, divergences

### Alarms

- High CPU (> 80%)
- High error rate (> 5%)
- Low matching accuracy (< 98.5%)
- Database connection pool exhausted

## Rollback Procedure

```bash
# 1. Get previous task definition
PREV_TASK_DEF=$(aws ecs describe-services \
  --cluster conciliaai-alpha \
  --services conciliaai-api \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

# 2. Update service to previous version
aws ecs update-service \
  --cluster conciliaai-alpha \
  --service conciliaai-api \
  --task-definition "$PREV_TASK_DEF"

# 3. Wait for stabilization
aws ecs wait services-stable \
  --cluster conciliaai-alpha \
  --services conciliaai-api
```

## Cost Monitoring

### Phase 1 (Alpha) - Expected Costs

| Service | Monthly Cost (BRL) |
|---------|-------------------|
| ECS Fargate | R$ 30 |
| RDS PostgreSQL | R$ 50 |
| ElastiCache Redis | R$ 20 |
| ALB | R$ 25 |
| NAT Gateway | R$ 15 |
| CloudWatch | R$ 10 |
| **Total** | **~R$ 150** |

Monitor actual costs:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```
