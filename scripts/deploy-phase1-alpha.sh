#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/common/logging.sh"
source "$SCRIPT_DIR/common/validation.sh"

ENVIRONMENT="alpha"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"

log_section "🚀 Deploying ConciliaAI - Phase 1 Alpha"

log_info "Validating prerequisites..."
require_command aws
require_command terraform
require_command docker
log_success "Prerequisites validated"

log_section "Building Docker image..."
cd "$PROJECT_ROOT"

docker build \
    -t conciliaai-api:latest \
    -f Dockerfile \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    .

log_success "Docker image built"

log_section "Pushing to Amazon ECR..."
ECR_REPO=$(aws ecr describe-repositories \
    --repository-names conciliaai-api \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" \
    --query 'repositories[0].repositoryUri' \
    --output text 2>/dev/null || echo "")

if [[ -z "$ECR_REPO" ]]; then
    log_info "Creating ECR repository..."
    ECR_REPO=$(aws ecr create-repository \
        --repository-name conciliaai-api \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --query 'repository.repositoryUri' \
        --output text)
fi

aws ecr get-login-password \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" | \
docker login \
    --username AWS \
    --password-stdin \
    "$ECR_REPO"

docker tag conciliaai-api:latest "$ECR_REPO:latest"
TIMESTAMP_TAG="$ECR_REPO:alpha-$(date +%Y%m%d-%H%M%S)"
docker tag conciliaai-api:latest "$TIMESTAMP_TAG"

docker push "$ECR_REPO:latest"
docker push "$TIMESTAMP_TAG"

log_success "Image pushed to ECR: $ECR_REPO"

log_section "Running database migrations..."
cd "$PROJECT_ROOT/migrations"

RDS_ENDPOINT=$(aws rds describe-db-clusters \
    --db-cluster-identifier conciliaai-alpha \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" \
    --query 'DBClusters[0].Endpoint' \
    --output text 2>/dev/null || echo "")

if [[ -z "$RDS_ENDPOINT" ]]; then
    log_warn "RDS cluster not found. It will be created by Terraform."
else
    log_info "Running migrations on $RDS_ENDPOINT..."
    DB_PASSWORD=$(aws secretsmanager get-secret-value \
        --secret-id conciliaai/alpha/db-password \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --query 'SecretString' \
        --output text)

    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$RDS_ENDPOINT" \
        -U conciliaai_admin \
        -d conciliaai \
        -f 001_initial_schema.sql

    log_success "Migrations completed"
fi

log_section "Deploying infrastructure with Terraform..."
cd "$PROJECT_ROOT/infrastructure/terraform"

terraform init \
    -backend-config="bucket=conciliaai-terraform-state" \
    -backend-config="key=$ENVIRONMENT/terraform.tfstate" \
    -backend-config="region=$AWS_REGION"

terraform plan \
    -var="environment=$ENVIRONMENT" \
    -var="aws_region=$AWS_REGION" \
    -var="db_instance_class=db.t4g.micro" \
    -out=tfplan

terraform apply tfplan

log_success "Infrastructure deployed"

log_section "Updating ECS service..."
aws ecs update-service \
    --cluster conciliaai-$ENVIRONMENT \
    --service conciliaai-api \
    --force-new-deployment \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE"

log_info "Waiting for service to stabilize..."
aws ecs wait services-stable \
    --cluster conciliaai-$ENVIRONMENT \
    --services conciliaai-api \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE"

log_success "ECS service updated"

log_section "Running health checks..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names conciliaai-api-$ENVIRONMENT \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

log_info "ALB DNS: $ALB_DNS"

sleep 30

HEALTH_URL="https://$ALB_DNS/health"
for attempt in {1..10}; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")
    if [[ "$HTTP_STATUS" == "200" ]]; then
        log_success "Health check passed!"
        break
    else
        log_warn "Health check attempt $attempt/10 failed (HTTP $HTTP_STATUS)"
        sleep 10
    fi
done

if [[ "$HTTP_STATUS" != "200" ]]; then
    log_error "Health check failed after 10 attempts"
    exit 1
fi

log_section "Running smoke tests..."
python3 "$PROJECT_ROOT/tests/smoke/test_api.py" \
    --base-url "https://$ALB_DNS" \
    --environment "$ENVIRONMENT"

log_success "Smoke tests passed"

log_section "🎉 Deployment Complete!"

printf '\nEnvironment: %s\n' "$ENVIRONMENT"
printf 'API URL: https://%s\n' "$ALB_DNS"
printf 'Region: %s\n' "$AWS_REGION"
printf '\nEstimated cost: ~R$ 150/mês\n\n'
printf 'Next steps:\n'
printf '1. Configure DNS: Point conciliaai-api.yourdomain.com → %s\n' "$ALB_DNS"
printf '2. Setup SSL certificate in ACM\n'
printf '3. Configure monitoring alerts\n'
printf '4. Onboard first tenant\n\n'
