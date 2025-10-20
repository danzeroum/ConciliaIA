📘 ConciliaAI v7.0 - Operations Runbook
Guia operacional para o time de SRE/DevOps.
🚨 Emergency Contacts

On-Call Engineer: +55 11 9999-1111
Team Lead: +55 11 9999-2222
Database Admin: +55 11 9999-3333
Security Team: +55 11 9999-4444

Escalation Matrix:

On-Call Engineer (0-15 min)
Team Lead (15-30 min)
CTO (30+ min)


🎯 Common Operations
1. Check System Health
```bash
# Quick health check
curl https://api.conciliaai.com/health

# Check all pods
kubectl get pods -n conciliaai-prod

# Check recent events
kubectl get events -n conciliaai-prod --sort-by='.lastTimestamp' | tail -20

# Check logs (last 100 lines)
kubectl logs -n conciliaai-prod deployment/conciliaai-api --tail=100

# Check metrics
curl http://prometheus:9090/api/v1/query?query=up{job="conciliaai-api"}
```
2. Scale Application
```bash
# Manual scaling
kubectl scale deployment conciliaai-api \
  --replicas=5 \
  -n conciliaai-prod

# Check HPA status
kubectl get hpa -n conciliaai-prod

# Update HPA
kubectl patch hpa conciliaai-api-hpa \
  -n conciliaai-prod \
  --patch '{"spec":{"minReplicas":5,"maxReplicas":15}}'
```
3. Database Operations
```bash
# Connect to database
kubectl run psql-client \
  --image=postgres:16-alpine \
  --rm -it \
  --restart=Never \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -- psql -h $DB_HOST -U $DB_USER -d conciliaai
```
```sql
# Check connection pool
SELECT 
  count(*) as total_connections,
  sum(case when state = 'active' then 1 else 0 end) as active,
  sum(case when state = 'idle' then 1 else 0 end) as idle
FROM pg_stat_activity
WHERE datname = 'conciliaai';

# Find slow queries
SELECT 
  query,
  mean_exec_time,
  calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

# Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
4. Apply Migrations
```bash
# Check current migration version
kubectl exec -it -n conciliaai-prod \
  deployment/conciliaai-api -- \
  alembic current

# Upgrade to head
kubectl exec -it -n conciliaai-prod \
  deployment/conciliaai-api -- \
  alembic upgrade head

# Rollback one migration
kubectl exec -it -n conciliaai-prod \
  deployment/conciliaai-api -- \
  alembic downgrade -1
```
5. View Logs
```bash
# Real-time logs (all pods)
kubectl logs -f -n conciliaai-prod deployment/conciliaai-api

# Logs from specific pod
kubectl logs -f -n conciliaai-prod pod/conciliaai-api-abc123-xyz

# Search for errors (last 1 hour)
kubectl logs -n conciliaai-prod deployment/conciliaai-api --since=1h | grep ERROR

# Export logs to file
kubectl logs -n conciliaai-prod deployment/conciliaai-api --since=24h > logs.txt
```

🔥 Incident Response

### High Error Rate
**Symptom:** Error rate > 1%

**Investigation:**
```bash
# Check error logs
kubectl logs -n conciliaai-prod deployment/conciliaai-api --since=15m | grep "ERROR\|CRITICAL"

# Check metrics
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])"

# Check database
kubectl exec -it postgres-client -- psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```
**Common Causes:**
- Database connection pool exhausted
- External API (acquirer) timeout
- Memory leak causing OOM
- Bug in recent deployment

**Resolution:**
```bash
# If database issue:
kubectl scale deployment conciliaai-api --replicas=5  # Reduce load
# Increase connection pool in configmap

# If external API issue:
# Check acquirer status pages
# Implement circuit breaker if not active

# If memory leak:
kubectl rollout undo deployment/conciliaai-api  # Rollback
# Investigate with memory profiler

# If recent deployment:
kubectl rollout undo deployment/conciliaai-api
```

### High Latency
**Symptom:** P95 latency > 500ms

**Investigation:**
```bash
# Check pod resources
kubectl top pods -n conciliaai-prod

# Check database performance
# Connect to DB and run:
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Check for slow endpoints
kubectl logs -n conciliaai-prod deployment/conciliaai-api | grep "duration_ms" | sort -t: -k4 -nr | head -20
```
**Resolution:**
```bash
# Scale up
kubectl scale deployment conciliaai-api --replicas=8

# Add database indexes (if missing)
# Check query plans for slow queries

# Enable caching (if not already)
# Review and optimize slow endpoints
```

### Database Connection Issues
**Symptom:** connection refused or too many connections

**Investigation:**
```bash
# Check database status
kubectl exec -it postgres-client -- pg_isready -h $DB_HOST

# Check connections
kubectl exec -it postgres-client -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check pool status in application
kubectl logs -n conciliaai-prod deployment/conciliaai-api | grep "pool"
```
**Resolution:**
```bash
# Restart pods (rolling restart)
kubectl rollout restart deployment/conciliaai-api -n conciliaai-prod

# Increase max_connections in PostgreSQL
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();

# Increase pool size in application
# Edit configmap and restart pods
```

### Pod Crashes (CrashLoopBackOff)
**Investigation:**
```bash
# Check pod status
kubectl describe pod -n conciliaai-prod conciliaai-api-abc123-xyz

# Check logs from crashed container
kubectl logs -n conciliaai-prod --previous conciliaai-api-abc123-xyz

# Check events
kubectl get events -n conciliaai-prod --sort-by='.lastTimestamp'
```
**Common Causes:**
- OOMKilled (memory limit exceeded)
- Database migration failure
- Missing secrets/configmaps
- Application startup error

**Resolution:**
```bash
# If OOMKilled:
kubectl patch deployment conciliaai-api \
  -n conciliaai-prod \
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"4Gi"}}}]}}}}'

# If migration failure:
kubectl exec -it -n conciliaai-prod deployment/conciliaai-api -- alembic downgrade -1
# Fix migration and redeploy

# If missing secrets:
kubectl get secret conciliaai-secrets -n conciliaai-prod
# Recreate if missing

# If startup error:
kubectl logs -n conciliaai-prod deployment/conciliaai-api --previous
# Fix configuration and redeploy
```

### Certificate Expiration
**Symptom:** TLS/SSL errors

**Investigation:**
```bash
# Check certificate expiration
kubectl get certificate -n conciliaai-prod

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manual check
echo | openssl s_client -servername api.conciliaai.com -connect api.conciliaai.com:443 2>/dev/null | openssl x509 -noout -dates
```
**Resolution:**
```bash
# Force renewal
kubectl delete certificate conciliaai-tls -n conciliaai-prod
# cert-manager will auto-recreate

# Or manually trigger
kubectl annotate certificate conciliaai-tls -n conciliaai-prod cert-manager.io/issue-temporary-certificate="true"
```

📊 Performance Tuning

### Database Optimization
```sql
-- Analyze tables
ANALYZE sales;
ANALYZE acquirer_transactions;
ANALYZE reconciliation_matches;

-- Vacuum full (during maintenance window)
VACUUM FULL ANALYZE;

-- Check for missing indexes
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.9
ORDER BY n_distinct DESC;

-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan;
```

### Application Tuning
```bash
# Update connection pool size
kubectl edit configmap conciliaai-config -n conciliaai-prod
# Set: pool_size: 30, max_overflow: 60

# Enable query caching
# Update configmap:
# ENABLE_CACHE=true
# CACHE_TTL=300

# Adjust worker processes
# Update deployment:
# API_WORKERS=4

# Restart to apply
kubectl rollout restart deployment/conciliaai-api -n conciliaai-prod
```

🔄 Backup & Restore

### Database Backup
```bash
# Manual backup
kubectl run pg-backup \
  --image=postgres:16-alpine \
  --rm -it \
  --restart=Never \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -- pg_dump -h $DB_HOST -U $DB_USER -d conciliaai -F c -f /tmp/backup.dump
```
```bash
# Automated daily backup (CronJob)
kubectl apply -f - <<'YAML'
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: conciliaai-prod
spec:
  schedule: "0 3 * * *"  # 3 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: conciliaai-secrets
                  key: DB_PASSWORD
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h $DB_HOST -U $DB_USER -d conciliaai -F c | \
              aws s3 cp - s3://conciliaai-backups/db-backup-$(date +%Y%m%d-%H%M%S).dump
          restartPolicy: OnFailure
YAML
```

### Restore from Backup
```bash
# Download backup
aws s3 cp s3://conciliaai-backups/db-backup-20250119-030000.dump ./backup.dump

# Restore
kubectl run pg-restore \
  --image=postgres:16-alpine \
  --rm -it \
  --restart=Never \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -- pg_restore -h $DB_HOST -U $DB_USER -d conciliaai_restored -F c backup.dump

# Or point-in-time recovery (AWS RDS)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier conciliaai-prod \
  --target-db-instance-identifier conciliaai-restored \
  --restore-time 2025-01-19T10:00:00Z
```

🔒 Security Operations

### Rotate Secrets
```bash
# Generate new JWT secret
NEW_SECRET=$(openssl rand -hex 32)

# Update secret
kubectl create secret generic conciliaai-secrets-new \
  --from-literal=SECRET_KEY=$NEW_SECRET \
  --from-literal=DATABASE_URL=$DATABASE_URL \
  -n conciliaai-prod --dry-run=client -o yaml | kubectl apply -f -

# Update deployment to use new secret
kubectl patch deployment conciliaai-api \
  -n conciliaai-prod \
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"api","envFrom":[{"secretRef":{"name":"conciliaai-secrets-new"}}]}]}}}}'

# Rollout restart
kubectl rollout restart deployment/conciliaai-api -n conciliaai-prod

# Verify
kubectl rollout status deployment/conciliaai-api -n conciliaai-prod

# Delete old secret after validation
kubectl delete secret conciliaai-secrets -n conciliaai-prod
```

### Security Audit
```bash
# Check for vulnerabilities in images
trivy image conciliaai/backend:7.0.0

# Check for secrets in logs
kubectl logs -n conciliaai-prod deployment/conciliaai-api | grep -i "password\|secret\|key"
# Should return nothing

# Check RBAC
kubectl auth can-i --list -n conciliaai-prod

# Check network policies
kubectl get networkpolicies -n conciliaai-prod

# Check pod security policies
kubectl get psp
```

📞 Monitoring & Alerting

### Key Alerts
**Critical Alerts (Page immediately):**

- API down (all pods unhealthy)
- Error rate > 5%
- P95 latency > 1s
- Database down
- Accuracy < 95%

**Warning Alerts (Slack notification):**

- Error rate > 1%
- P95 latency > 500ms
- Memory usage > 90%
- CPU usage > 90%
- Disk usage > 85%

**Info Alerts (Log only):**

- Deployment started/completed
- Scale up/down
- Certificate renewal

### Check Alert Status
```bash
# View active alerts
curl http://alertmanager:9093/api/v1/alerts | jq '.data[] | select(.status.state=="active")'

# Silence alert (maintenance)
amtool silence add alertname="HighLatency" --duration=2h --comment="Planned maintenance"

# Check silences
amtool silence query

# Remove silence
amtool silence expire <silence_id>
```

📈 Capacity Planning

### Resource Usage Trends
```bash
# CPU usage (last 7 days)
kubectl top nodes
kubectl top pods -n conciliaai-prod

# Memory usage
kubectl describe node | grep -A 5 "Allocated resources"

# Storage usage
df -h /data

# Database size growth
psql -c "SELECT pg_size_pretty(pg_database_size('conciliaai'));"
```

### Scaling Recommendations
Current Load (as of 2025-01-19):

- Request Rate: 125 req/s (peak: 200 req/s)
- Active Users: 1,245 concurrent
- Database Size: 50GB
- Daily Growth: ~500MB

**Scaling Thresholds:**

Scale Up when:

- CPU usage > 70% for 5 minutes
- Memory usage > 80% for 5 minutes
- Request queue > 100
- P95 latency > 200ms

Scale Down when:

- CPU usage < 30% for 15 minutes
- Memory usage < 40% for 15 minutes
- Request queue < 10
- Min replicas not reached

Future Capacity (6 months projection):

- Expected Users: 3,000 concurrent
- Expected Request Rate: 300 req/s
- Expected Database Size: 150GB

**Recommended Resources:**

- API Pods: 6-15 replicas
- Database: db.r6g.xlarge (4 vCPU, 32GB RAM)
- Storage: 250GB with auto-scaling

🛠️ Maintenance Windows

### Planned Maintenance Procedure
**Pre-Maintenance (1 week before):**
```bash
# 1. Notify users
# 2. Create backup
# 3. Test changes in staging
# 4. Prepare rollback plan
# 5. Update runbook if needed
```

**Maintenance Window (Sunday 2-5 AM):**
```bash
# 1. Enable maintenance mode
kubectl scale deployment conciliaai-api --replicas=0 -n conciliaai-prod

# 2. Create database backup
pg_dump -h $DB_HOST -U $DB_USER -d conciliaai -F c > backup-maintenance.dump

# 3. Apply migrations
alembic upgrade head

# 4. Apply infrastructure changes
kubectl apply -f k8s/production/

# 5. Scale up
kubectl scale deployment conciliaai-api --replicas=3 -n conciliaai-prod

# 6. Verify health
kubectl rollout status deployment/conciliaai-api -n conciliaai-prod
curl https://api.conciliaai.com/health

# 7. Run smoke tests
./scripts/smoke-tests.sh production

# 8. Monitor for 30 minutes
watch kubectl get pods -n conciliaai-prod

# 9. Disable maintenance mode
# 10. Notify users
```

📚 Useful Commands Cheat Sheet
```bash
# === Quick Status ===
kubectl get all -n conciliaai-prod
kubectl get events -n conciliaai-prod --sort-by='.lastTimestamp' | tail -20
kubectl top pods -n conciliaai-prod

# === Logs ===
kubectl logs -f deployment/conciliaai-api -n conciliaai-prod
kubectl logs deployment/conciliaai-api -n conciliaai-prod --since=1h | grep ERROR

# === Exec into Pod ===
kubectl exec -it deployment/conciliaai-api -n conciliaai-prod -- /bin/bash

# === Port Forward ===
kubectl port-forward -n conciliaai-prod deployment/conciliaai-api 8000:8000

# === Restart ===
kubectl rollout restart deployment/conciliaai-api -n conciliaai-prod

# === Rollback ===
kubectl rollout undo deployment/conciliaai-api -n conciliaai-prod

# === Scale ===
kubectl scale deployment conciliaai-api --replicas=5 -n conciliaai-prod

# === Config ===
kubectl edit configmap conciliaai-config -n conciliaai-prod
kubectl edit secret conciliaai-secrets -n conciliaai-prod

# === Database ===
kubectl run psql-client --image=postgres:16-alpine --rm -it --restart=Never \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -- psql -h $DB_HOST -U $DB_USER -d conciliaai
```

---

## 🆘 Escalation Procedures

### Level 1 - On-Call Engineer (0-15 min)
- Investigate alerts
- Check logs and metrics
- Apply standard fixes
- Communicate in Slack #incidents

### Level 2 - Team Lead (15-30 min)
- Review investigation
- Coordinate resources
- Make architectural decisions
- Approve rollbacks/changes

### Level 3 - CTO/VP Engineering (30+ min)
- Critical system failure
- Data breach
- Customer-impacting outage > 30 min
- Financial impact > $10k

**Incident Communication Template:**
```
[INCIDENT] <Severity> - <Title>

Status: INVESTIGATING | MITIGATING | RESOLVED
Started: 2025-01-19 10:30 UTC
Impact: <User impact description>

Timeline:
- 10:30: Alert triggered
- 10:32: Investigation started
- 10:35: Root cause identified
- 10:40: Fix applied
- 10:45: Monitoring for stability

Root Cause: <Brief description>
Resolution: <What was done>
Next Steps: <Follow-up actions>

Incident Commander: @engineer

Last Updated: 2025-10-19
Version: 7.0.0
Maintained by: SRE Team
```
