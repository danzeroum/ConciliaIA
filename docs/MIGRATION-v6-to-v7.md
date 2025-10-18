# 🔄 BuildToValue v7.0 - Migration Guide (v6 → v7)

Complete guide for migrating existing BuildToFlip v6 projects to BuildToValue v7.

## 📑 Table of Contents

1. [Overview](#overview)
2. [What's New in v7](#whats-new-in-v7)
3. [Breaking Changes](#breaking-changes)
4. [Pre-Migration Checklist](#pre-migration-checklist)
5. [Automated Migration](#automated-migration)
6. [Manual Migration Steps](#manual-migration-steps)
7. [Post-Migration Tasks](#post-migration-tasks)
8. [Rollback Procedure](#rollback-procedure)
9. [FAQ](#faq)
10. [Support](#support)

---

## Overview

### Migration Timeline

| Project Size | Estimated Time | Complexity |
|--------------|----------------|------------|
| **Small** (< 10k LOC) | 2-4 hours | Low |
| **Medium** (10k-50k LOC) | 1 day | Medium |
| **Large** (50k-200k LOC) | 2-3 days | Medium-High |
| **Enterprise** (200k+ LOC) | 1 week | High |

### Compatibility

- ✅ **Data**: 100% compatible - no data loss
- ✅ **Configuration**: 95% compatible - minor adjustments
- ✅ **Scripts**: 80% compatible - some renamed
- ⚠️ **Custom Code**: Depends on customizations

### Support

- **Automated Script**: Handles 90% of migration
- **Manual Steps**: Required for customizations
- **Community Help**: Discord support available
- **Professional Services**: Available for enterprise

---

## What's New in v7

### Major Enhancements
```yaml
new_features_v7:
  
  expanded_squad:
    from: "5 basic IAs"
    to: "11 specialized IAs with mental models"
    new_ias:
      - "IA-Business-Analyst"
      - "IA-Data-Architect"
      - "IA-Integration-Specialist"
      - "IA-Ethics-Guardian"
  
  mental_models:
    description: "Each IA now has explicit mental models based on books"
    examples:
      - "IA-Developer: Clean Code, Pragmatic Programmer"
      - "IA-Auditor: Web App Hacker's Handbook, OWASP"
  
  smart_orchestration:
    description: "ML-based routing with confidence scoring"
    features:
      - "Automatic IA selection"
      - "Historical learning (Auto-RAG)"
      - "Cost optimization"
      - "Conflict prediction"
  
  autonomy_system:
    description: "Progressive autonomy levels (L1-L5)"
    features:
      - "Performance-based adjustment"
      - "Domain-specific autonomy"
      - "Automatic escalation"
  
  inter_ia_communication:
    description: "Direct communication between IAs"
    protocols:
      - "Consultation"
      - "Alert"
      - "Suggestion"
      - "Broadcast"
  
  observability:
    description: "Enhanced monitoring and dashboards"
    tools:
      - "Grafana dashboards (5 pre-built)"
      - "Distributed tracing (Jaeger)"
      - "Business metrics tracking"
      - "Squad health monitoring"
  
  learning_system:
    description: "Continuous improvement"
    features:
      - "Auto-RAG with semantic search"
      - "Lessons learned capture"
      - "A/B testing framework"
      - "Pattern recognition"
```

### Renamed Components

| v6 Name | v7 Name | Reason |
|---------|---------|--------|
| `.buildtoflip/` | `.buildtovalue/` | Reflects value focus |
| `discovery-consensus.v6.json` | `discovery-consensus.v7.json` | Version increment |
| `gates-v6.sh` | `gates-v7.sh` | Version increment |
| `IA-Dev` | `IA-Developer` | Clarity |
| `IA-Designer` | `IA-Designer` | No change |

---

## Breaking Changes

### Critical (Action Required)
```yaml
breaking_changes:
  
  directory_structure:
    change: ".buildtoflip → .buildtovalue"
    impact: "All paths updated"
    action: "Automated migration handles this"
    manual_action: "Update any custom scripts referencing old path"
  
  consensus_schema:
    change: "New fields added to discovery-consensus"
    impact: "Old format still readable, but should upgrade"
    action: "Automated script converts"
    new_fields:
      - "project_type: standard | ai_agent"
      - "orchestration_mode: manual | assisted | autonomous"
      - "cost_constraints"
  
  quality_gates:
    change: "New gates added"
    impact: "More stringent quality requirements"
    action: "Review and adjust thresholds if needed"
    new_gates:
      - "Squad efficiency metrics"
      - "Business metrics"
      - "Learning system health"
  
  docker_compose:
    change: "New services added"
    impact: "More containers = more resources"
    action: "Ensure 8GB+ RAM available"
    new_services:
      - "ChromaDB (vector database)"
      - "Jaeger (tracing)"
```

### Non-Breaking (Recommended Updates)
```yaml
recommended_updates:
  
  personas:
    change: "Add mental models to existing personas"
    impact: "Better decision quality"
    action: "Run: ./scripts/migration/add-mental-models.sh"
  
  activation_matrix:
    change: "Expand with new semantic patterns"
    impact: "Better routing accuracy"
    action: "Review: .buildtovalue/orchestration/activation-matrix.yaml"
  
  observability:
    change: "Enable new dashboards"
    impact: "Better visibility"
    action: "Import Grafana dashboards from templates/"
```

---

## Pre-Migration Checklist

### Before You Start
```bash
# 1. Check current version
cat .buildtoflip/consensus/discovery-consensus.v6.json | grep version
# Should show: "version": "6.0"

# 2. Verify git status (clean working directory)
git status
# Should show: "nothing to commit, working tree clean"

# 3. Check disk space (need ~5GB free)
df -h
# Ensure / partition has 5GB+ available

# 4. Check RAM (need 8GB+ for v7)
free -h
# Ensure 8GB+ total

# 5. Backup current database
./scripts/backup-v6-state.sh
# Creates: backups/v6-backup-TIMESTAMP.tar.gz

# 6. Tag current version in git
git tag v6-final
git push origin v6-final

# 7. Create migration branch
git checkout -b migrate-to-v7

# 8. Verify all services running
docker-compose ps
# All should show "Up"

# 9. Run final v6 gates
./scripts/gates-v6.sh --full
# Should all pass before migration

# 10. Export current metrics (for comparison)
./scripts/monitoring/export-metrics.sh \
  --period=last-month \
  --output=v6-metrics-baseline.json
```

### Checklist Summary

- [ ] Git working directory is clean
- [ ] Current version backed up
- [ ] Git tag created (v6-final)
- [ ] Migration branch created
- [ ] 8GB+ RAM available
- [ ] 5GB+ disk space available
- [ ] All v6 quality gates passing
- [ ] Baseline metrics exported
- [ ] Team notified of migration
- [ ] Downtime window scheduled (if needed)

---

## Automated Migration

### Quick Migration (Recommended)
```bash
# Download and run migration script
curl -fsSL https://raw.githubusercontent.com/buildtovalue/v7/main/scripts/migrate-v6-to-v7.sh -o migrate.sh
chmod +x migrate.sh

# Run with interactive prompts
./migrate.sh --interactive

# Or run non-interactive with defaults
./migrate.sh --auto-approve

# Expected output:
# 🔄 BuildToFlip v6 → BuildToValue v7 Migration
# ════════════════════════════════════════════════════
# 
# Pre-flight checks:
#   ✅ Git working directory clean
#   ✅ Backup exists (v6-backup-20250120.tar.gz)
#   ✅ Disk space: 15.2GB available
#   ✅ RAM: 16GB available
#   ✅ Docker running
# 
# Phase 1: Backup (2 minutes)
#   ✅ Database backup complete
#   ✅ Configuration backup complete
#   ✅ Ledger backup complete
#   ✅ Git tag created: v6-final
# 
# Phase 2: Structure Migration (5 minutes)
#   ✅ Renamed .buildtoflip → .buildtovalue
#   ✅ Updated all internal references
#   ✅ Converted consensus files to v7 schema
#   ✅ Migrated ledger format
# 
# Phase 3: Squad Enhancement (10 minutes)
#   ✅ Created 6 new persona files
#   ✅ Added mental models to existing personas
#   ✅ Configured activation matrix
#   ✅ Setup orchestration layer
# 
# Phase 4: Infrastructure (15 minutes)
#   ✅ Updated docker-compose-v7.yml
#   ✅ Pulled new images (ChromaDB, Jaeger)
#   ✅ Started new services
#   ✅ Initialized ChromaDB
#   ✅ Configured Prometheus
#   ✅ Imported Grafana dashboards
# 
# Phase 5: Learning System (5 minutes)
#   ✅ Built Auto-RAG index from existing decisions
#   ✅ Indexed 1,247 decisions
#   ✅ Created embeddings
#   ✅ Validated retrieval (accuracy: 92%)
# 
# Phase 6: Validation (3 minutes)
#   ✅ All services healthy
#   ✅ 11/11 personas loaded
#   ✅ Database schema migrated
#   ✅ Quality gates passing (95%)
#   ✅ Backward compatibility verified
# 
# Phase 7: Cleanup (1 minute)
#   ✅ Removed deprecated files
#   ✅ Updated .gitignore
#   ✅ Generated migration report
# 
# ════════════════════════════════════════════════════
# ✅ Migration Complete!
# 
# Summary:
#   Duration: 41 minutes
#   Decisions migrated: 1,247
#   New personas: 6
#   Warnings: 2 (see below)
# 
# ⚠️  Warnings:
#   1. Custom script found: scripts/custom-deploy.sh
#      → Update references to .buildtoflip → .buildtovalue
#   
#   2. docker-compose.override.yml detected
#      → Review and merge with docker-compose-v7.yml if needed
# 
# Next Steps:
#   1. Review warnings above
#   2. Test with: ./scripts/orchestrator/route-problem.sh "test"
#   3. View dashboard: http://localhost:3000
#   4. Read: docs/MIGRATION-v6-to-v7.md
#   5. Commit: git add . && git commit -m "Migrate to BuildToValue v7"
# 
# Rollback if needed:
#   ./scripts/rollback-to-v6.sh
```

### What the Script Does
```yaml
migration_script_phases:
  
  phase_1_backup:
    duration: "2 minutes"
    actions:
      - "Create full database backup"
      - "Backup all configuration files"
      - "Backup ledger and decisions"
      - "Create git tag v6-final"
    
    output: "backups/v6-backup-TIMESTAMP.tar.gz"
  
  phase_2_structure:
    duration: "5 minutes"
    actions:
      - "Rename .buildtoflip → .buildtovalue"
      - "Update file references"
      - "Convert consensus schema v6 → v7"
      - "Migrate ledger format"
      - "Update decision IDs format"
    
    files_affected: "~200 files"
  
  phase_3_squad:
    duration: "10 minutes"
    actions:
      - "Create 6 new persona files"
      - "Add mental models to existing 5 personas"
      - "Generate activation matrix"
      - "Configure routing rules"
      - "Setup inter-IA communication protocols"
    
    output: ".buildtovalue/squad/"
  
  phase_4_infrastructure:
    duration: "15 minutes"
    actions:
      - "Update Docker Compose to v7"
      - "Pull new container images"
      - "Start ChromaDB service"
      - "Start Jaeger service"
      - "Configure Prometheus for new metrics"
      - "Import 5 Grafana dashboards"
    
    new_services: ["chromadb", "jaeger"]
  
  phase_5_learning:
    duration: "5 minutes"
    actions:
      - "Read all existing decisions from ledger"
      - "Generate embeddings using sentence-transformers"
      - "Build ChromaDB index"
      - "Validate retrieval accuracy"
    
    output: ".buildtovalue/learning/rag-index/"
  
  phase_6_validation:
    duration: "3 minutes"
    actions:
      - "Health check all services"
      - "Validate all personas load"
      - "Test database connection"
      - "Run quality gates"
      - "Verify backward compatibility"
    
    critical: "Migration fails if validation doesn't pass"
  
  phase_7_cleanup:
    duration: "1 minute"
    actions:
      - "Remove deprecated v6-specific files"
      - "Update .gitignore"
      - "Generate migration report"
      - "Create rollback script"
```

---

## Manual Migration Steps

### If Automated Migration Fails

Follow these steps manually if the automated script encounters issues.

### Step 1: Backup
```bash
# Create full backup
mkdir -p backups/v6-manual-backup

# Database
docker exec buildtoflip-postgres pg_dump -U btv_user buildtoflip > \
  backups/v6-manual-backup/database.sql

# Files
tar -czf backups/v6-manual-backup/files.tar.gz \
  .buildtoflip/ \
  docs/ \
  scripts/ \
  .env.dev \
  docker-compose.yml

# Git tag
git tag v6-final-manual
git push origin v6-final-manual
```

### Step 2: Rename Directory Structure
```bash
# Rename main directory
mv .buildtoflip .buildtovalue

# Update git tracking
git mv .buildtoflip .buildtovalue

# Update all file references
find . -type f -name "*.sh" -exec sed -i 's/\.buildtoflip/\.buildtovalue/g' {} +
find . -type f -name "*.py" -exec sed -i 's/\.buildtoflip/\.buildtovalue/g' {} +
find . -type f -name "*.md" -exec sed -i 's/buildtoflip/buildtovalue/g' {} +

# Update environment files
sed -i 's/buildtoflip/buildtovalue/g' .env.dev
sed -i 's/buildtoflip/buildtovalue/g' .env.example
```

### Step 3: Update Consensus Files
```bash
# Backup original
cp .buildtovalue/consensus/discovery-consensus.v6.json \
   .buildtovalue/consensus/discovery-consensus.v6.backup.json

# Update schema
cat > /tmp/update-consensus.py << 'PYEOF'
import json

# Read v6
with open('.buildtovalue/consensus/discovery-consensus.v6.json', 'r') as f:
    data = json.load(f)

# Update to v7
data['version'] = '7.0'
data['orchestration'] = {
    'mode': 'assisted',
    'confidence_threshold': 0.75
}
data['cost_constraints'] = {
    'daily_limit': 10.0,
    'per_decision_limit': 0.20
}

# Write v7
with open('.buildtovalue/consensus/discovery-consensus.v7.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Consensus file updated to v7")
PYEOF

python3 /tmp/update-consensus.py
```

### Step 4: Create New Persona Files
```bash
# Create directory
mkdir -p .buildtovalue/squad/personas

# Download persona templates
for persona in product-manager business-analyst arquiteto developer qa auditor designer ops data-architect integration-specialist ethics-guardian; do
  curl -fsSL https://raw.githubusercontent.com/buildtovalue/v7/main/templates/personas/ia-${persona}.yaml \
    -o .buildtovalue/squad/personas/ia-${persona}.yaml
done

# Validate
ls -l .buildtovalue/squad/personas/
# Should show 11 .yaml files
```

### Step 5: Update Docker Compose
```bash
# Backup old
cp docker-compose.yml docker-compose-v6.backup.yml

# Download v7 version
curl -fsSL https://raw.githubusercontent.com/buildtovalue/v7/main/docker/docker-compose-v7.yml \
  -o docker-compose.yml

# Or manually add new services to existing file
cat >> docker-compose.yml << 'YAMLEOF'

  chromadb:
    image: chromadb/chroma:latest
    container_name: buildtovalue-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    networks:
      - buildtovalue-network

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: buildtovalue-jaeger
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # HTTP collector
    networks:
      - buildtovalue-network

volumes:
  chromadb_data:

YAMLEOF

# Start new services
docker-compose up -d chromadb jaeger
```

### Step 6: Initialize Learning System
```bash
# Create directory
mkdir -p .buildtovalue/learning/rag-index

# Build RAG index from existing decisions
cat > /tmp/build-rag.py << 'PYE'
import json
import glob
from sentence_transformers import SentenceTransformer
import chromadb

# Initialize
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.create_collection('decisions')

# Read decisions
decisions = []
for file in glob.glob('.buildtovalue/ledger/decisions/*.jsonl'):
    with open(file, 'r') as f:
        for line in f:
            decisions.append(json.loads(line))

print(f"Found {len(decisions)} decisions")

# Index
for i, decision in enumerate(decisions):
    text = f"{decision['problem']} {decision['rationale']}"
    embedding = model.encode(text)
    
    collection.add(
        embeddings=[embedding.tolist()],
        documents=[text],
        metadatas=[{
            'id': decision['id'],
            'ia': decision['routing']['primary_ia'],
            'success': decision['outcome']['success']
        }],
        ids=[decision['id']]
    )
    
    if (i + 1) % 100 == 0:
        print(f"Indexed {i + 1}/{len(decisions)}")

print("✅ RAG index built successfully")
PYE

python3 /tmp/build-rag.py
```

### Step 7: Import Grafana Dashboards
```bash
# Wait for Grafana to be ready
sleep 10

# Import dashboards
for dashboard in executive-overview squad-efficiency technical-health learning-evolution cost-finops; do
  curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @templates/grafana/${dashboard}.json
done

echo "✅ Dashboards imported"
```

### Step 8: Validate Migration
```bash
# Run health check
./scripts/troubleshooting/health-check.sh

# Expected output:
# ✅ System Status: HEALTHY
# ✅ 11/11 IAs loaded successfully
# ✅ All services running
# Overall Health: 100/100

# Run quality gates
./scripts/gates-v7.sh --full

# Test routing
./scripts/orchestrator/route-problem.sh "Test migration"
```

---

## Post-Migration Tasks

### 1. Review Custom Code
```bash
# Find custom scripts
find . -name "*.sh" -path "*/custom/*"
find . -name "*.py" -path "*/custom/*"

# Update references
# Old: .buildtoflip
# New: .buildtovalue
```

### 2. Update CI/CD Pipelines
```yaml
# Example: .github/workflows/buildtovalue.yml
name: BuildToValue v7 Pipeline

on: [push, pull_request]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Quality Gates
        run: ./scripts/gates-v7.sh --full  # Updated from gates-v6.sh
      
      - name: Check Squad Health
        run: ./scripts/monitoring/squad-health.sh
```

### 3. Update Documentation
```bash
# Update README
sed -i 's/BuildToFlip v6/BuildToValue v7/g' README.md
sed -i 's/buildtoflip/buildtovalue/g' README.md

# Update all docs
find docs/ -name "*.md" -exec sed -i 's/buildtoflip/buildtovalue/g' {} +
```

### 4. Configure Observability
```bash
# Import additional dashboards
./scripts/monitoring/import-dashboards.sh

# Configure alerts
./scripts/monitoring/configure-alerts.sh \
  --slack-webhook="your-webhook-url" \
  --email="team@company.com"

# Test alerts
./scripts/monitoring/test-alerts.sh
```

### 5. Customize Personas for Your Domain
```bash
# Edit personas
nano .buildtovalue/squad/personas/ia-developer.yaml

# Add domain-specific references
# Example for fintech:
#   - "Domain-Driven Design in Finance"
#   - "Patterns of Enterprise Application Architecture"

# Reload personas
./scripts/squad/reload-personas.sh

# Validate
./scripts/squad/validate-personas.sh
```

### 6. Update Team Documentation
```markdown
# Update team wiki/confluence

## Migration to BuildToValue v7 Complete

**Date:** 2025-01-20
**Duration:** 3 hours
**Impact:** None - backward compatible

### What Changed
- 11 AI personas (was 5)
- Smart orchestration with ML
- Enhanced monitoring

### New Commands
- `./scripts/orchestrator/route-problem.sh` - Route problems
- `./scripts/monitoring/squad-dashboard.sh` - View dashboard
- `./scripts/ledger/recent-decisions.sh` - View history

### Resources
- Documentation: docs/
- Dashboard: http://localhost:3000
- Discord: https://discord.gg/buildtovalue
```

### 7. Train Team
```bash
# Run interactive tutorial
./scripts/tutorials/v7-whats-new.sh

# Share with team:
# 1. docs/GETTING-STARTED.md
# 2. docs/ORCHESTRATION-GUIDE.md
# 3. Video: https://youtube.com/buildtovalue-v7-intro
```

---

## Rollback Procedure

### If Something Goes Wrong
```bash
# Quick rollback (< 5 minutes)
./scripts/rollback-to-v6.sh

# This script will:
# 1. Stop v7 services
# 2. Restore v6 database backup
# 3. Restore v6 configuration
# 4. Rename .buildtovalue → .buildtoflip
# 5. Start v6 services
# 6. Validate v6 working

# Manual rollback (if script fails):

# 1. Stop services
docker-compose down

# 2. Restore git
git reset --hard v6-final
git clean -fd

# 3. Restore database
docker exec -i buildtoflip-postgres psql -U btv_user buildtoflip < \
  backups/v6-backup-TIMESTAMP/database.sql

# 4. Restore files
tar -xzf backups/v6-backup-TIMESTAMP/files.tar.gz

# 5. Start v6
docker-compose -f docker-compose-v6.yml up -d

# 6. Verify
./scripts/gates-v6.sh
```

### When to Rollback

Consider rollback if:
- ❌ Critical functionality broken
- ❌ Performance significantly degraded (> 50%)
- ❌ Data corruption detected
- ❌ Team cannot adapt quickly enough
- ❌ Cost increased unexpectedly (> 100%)

Do NOT rollback for:
- ⚠️ Minor UI differences
- ⚠️ Need to learn new commands
- ⚠️ Temporary configuration issues
- ⚠️ Non-critical warnings

---

## FAQ

### General Questions

**Q: Will I lose any data during migration?**
A: No. Migration is 100% data-safe. All decisions, configurations, and history are preserved. We also create automatic backups.

**Q: Can I still use v6 after migrating?**
A: Yes, via rollback script. But v6 won't receive updates after v7 release.

**Q: How long will migration take?**
A: Automated: 30-60 minutes. Manual: 2-4 hours (first time).

**Q: Do I need downtime?**
A: For development: No downtime needed. For production: Recommend 1-hour maintenance window for safety.

**Q: What if migration fails halfway?**
A: Safe to retry. Script is idempotent and has checkpoints. Or use rollback script.

### Technical Questions

**Q: Will my custom scripts still work?**
A: Mostly yes. Just update `.buildtoflip` → `.buildtovalue` references.

**Q: Do I need to re-train anything?**
A: No. All existing decisions are automatically indexed into Auto-RAG.

**Q: Will quality gates be more strict?**
A: Some new gates added, but existing thresholds remain the same. You can adjust.

**Q: What about my CI/CD pipelines?**
A: Update script names (gates-v6.sh → gates-v7.sh) and paths (.buildtoflip → .buildtovalue).

**Q: Is v7 backward compatible with v6 APIs?**
A: Yes, for 6 months. Deprecated APIs will show warnings.

### Cost Questions

**Q: Will v7 cost more to run?**
A: Slightly (+10-20%) due to ML-based routing, but improved decision quality often reduces total project cost.

**Q: Can I control costs?**
A: Yes. Set limits in discovery-consensus.v7.json or via:
```bash
./scripts/orchestrator/set-cost-limit.sh --daily=10.00
```

**Q: What uses the most API calls?**
A: Smart routing (when enabled) and Auto-RAG searches. Both configurable.

### Support Questions

**Q: Where can I get help?**
A: 
1. Discord: https://discord.gg/buildtovalue (fastest)
2. GitHub Issues: https://github.com/buildtovalue/v7/issues
3. Email: support@buildtovalue.com

**Q: Is professional migration support available?**
A: Yes, for enterprise customers. Contact: enterprise@buildtovalue.com

**Q: What if I find a bug?**
A: Report on GitHub Issues with migration support bundle:
```bash
./scripts/troubleshooting/generate-support-bundle.sh
```

---

## Troubleshooting Migration

### Common Issues

**Issue: "Migration script not found"**
```bash
# Solution: Download script directly
curl -fsSL https://raw.githubusercontent.com/buildtovalue/v7/main/scripts/migrate-v6-to-v7.sh \
  -o migrate-v6-to-v7.sh
chmod +x migrate-v6-to-v7.sh
```

**Issue: "ChromaDB fails to start"**
```bash
# Check port 8000 not in use
sudo lsof -i :8000

# If occupied, change port in docker-compose.yml
nano docker-compose.yml
# Change: "8000:8000" → "8001:8000"

# Restart
docker-compose restart chromadb
```

**Issue: "Out of disk space"**
```bash
# Clean Docker
docker system prune -a

# Check space
df -h

# If still insufficient, consider:
# - Archiving old backups
# - Cleaning logs
# - Using external volume for ChromaDB
```

**Issue: "Personas fail to load"**
```bash
# Validate YAML syntax
./scripts/squad/validate-personas.sh

# Check logs
docker-compose logs app | grep persona

# Reload
./scripts/squad/reload-personas.sh
```

**Issue: "Quality gates failing after migration"**
```bash
# Check which gates fail
./scripts/gates-v7.sh --full --verbose

# If new gates (squad/business metrics):
# These are new in v7, may need baseline period

# Temporarily adjust thresholds
nano .buildtovalue/config/quality-gates.yaml

# Or run without new gates initially
./scripts/gates-v7.sh --exclude=squad,business
```

---

## Support

### Getting Help
```bash
# Generate diagnostic report
./scripts/troubleshooting/diagnostic-report.sh

# Generate support bundle (includes logs, config, etc)
./scripts/troubleshooting/generate-support-bundle.sh

# Share on Discord or attach to GitHub issue
```

### Community Resources

- **Discord**: https://discord.gg/buildtovalue
- **GitHub Discussions**: https://github.com/buildtovalue/v7/discussions
- **YouTube Tutorials**: https://youtube.com/@buildtovalue
- **Blog**: https://blog.buildtovalue.com

### Professional Services

For enterprise migrations:
- **Email**: enterprise@buildtovalue.com
- **Services**:
  - Migration planning & execution
  - Custom integration
  - Team training
  - Ongoing support

---

## Success Stories

> "Migrated our 100k LOC project in 4 hours. The automated script worked flawlessly. Love the new mental models feature!" 
> — *TechCorp Engineering Team*

> "The Auto-RAG system has reduced our decision time by 40%. Migration was smooth, highly recommend."
> — *StartupXYZ CTO*

> "We rolled back once to fix a custom integration, then re-migrated successfully. Great rollback support!"
> — *Enterprise Inc DevOps Lead*

---

**Document Version:** 7.0.0  
**Last Updated:** 2025-01-20  
**Maintained By:** BuildToValue Migration Team  

© 2025 BuildToValue | [Main Documentation](./README.md) | [GitHub](https://github.com/buildtovalue/v7)
