# 🚀 BuildToValue v7.0 - Getting Started Guide

Welcome to BuildToValue v7! This guide will help you get your first AI-powered development squad running in **less than 30 minutes**.

## 📑 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [First Problem Routing](#first-problem-routing)
4. [Understanding the Squad](#understanding-the-squad)
5. [Basic Workflows](#basic-workflows)
6. [Next Steps](#next-steps)
7. [Getting Help](#getting-help)

---

## Prerequisites

### Required Software
```bash
# Check if you have everything installed:
docker --version          # Need: 20.10+
docker-compose --version  # Need: 2.0+
git --version            # Need: 2.30+

# For Java projects:
java --version           # Need: 17+

# For Python projects:
python3 --version        # Need: 3.11+

# Check available resources:
free -h                  # Need: 8GB+ RAM
df -h                    # Need: 20GB+ disk space
```

### API Keys

You'll need **at least one** of these:

- **OpenAI API Key** (recommended): https://platform.openai.com/api-keys
- **Anthropic API Key**: https://console.anthropic.com/
- **Google AI API Key**: https://makersuite.google.com/app/apikey

💡 **Tip**: Start with OpenAI GPT-4 for best results. You can add others later.

---

## Quick Start (5 minutes)

### Step 1: Clone the Template
```bash
# Clone the v7 template repository
git clone https://github.com/buildtovalue/template-v7.git my-project
cd my-project

# Verify structure
ls -la
# You should see:
# .buildtovalue/
# docs/
# scripts/
# docker/
# README.md
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env.dev

# Edit with your API keys
nano .env.dev
```

**Minimum configuration needed in `.env.dev`:**
```bash
# Required: At least one LLM provider
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional
# GOOGLE_AI_API_KEY=your-key-here         # Optional

# Project settings
PROJECT_NAME=my-awesome-project
PROJECT_DOMAIN=saas  # Options: fintech, healthtech, saas, ecommerce, other
FOUNDATION_LEVEL=lite  # Options: lite, standard, enterprise

# Database (defaults are fine for local dev)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=buildtovalue
POSTGRES_USER=btv_user
POSTGRES_PASSWORD=change_me_in_production

# Optional: Observability (recommended)
ENABLE_METRICS=true
ENABLE_TRACING=true
```

### Step 3: Initialize Project
```bash
# Run initialization script
./scripts/init-v7.sh

# This script will:
# ✓ Validate prerequisites
# ✓ Create directory structure
# ✓ Initialize database
# ✓ Load AI personas
# ✓ Configure activation matrix
# ✓ Start Docker services
# ✓ Run health checks

# Expected output:
# 🏗️  BuildToValue v7 Initialization
# ════════════════════════════════════════════════════
# ✅ Prerequisites validated
# ✅ Directory structure created
# ✅ Docker services starting...
# ✅ PostgreSQL ready (5s)
# ✅ ChromaDB ready (3s)
# ✅ Redis ready (2s)
# ✅ Prometheus ready (4s)
# ✅ Grafana ready (6s)
# ✅ 11 AI personas loaded
# ✅ Activation matrix configured
# ✅ Health check passed
# 
# 🎉 BuildToValue v7 is ready!
# 
# Next steps:
# 1. Test with: ./scripts/orchestrator/route-problem.sh "Hello world"
# 2. View dashboard: http://localhost:3000 (admin/admin)
# 3. Read docs: ./docs/ORCHESTRATION-GUIDE.md
```

### Step 4: Verify Installation
```bash
# Run health check
./scripts/troubleshooting/health-check.sh

# Expected output:
# ✅ System Status: HEALTHY
# ✅ 11/11 IAs loaded successfully
# ✅ All services running
# Overall Health: 100/100
```

**If you see any errors**, check [Troubleshooting](#troubleshooting-installation) below.

---

## First Problem Routing

Let's route your first problem to the AI squad!

### Example 1: Simple Question
```bash
./scripts/orchestrator/route-problem.sh \
  "How should I implement user authentication?"

# Output:
# 🎯 Analysis Complete
# 
# Problem Type: security_implementation
# Complexity: high
# 
# 🤖 Recommended Squad:
#   Primary: IA-Auditor (confidence: 0.92)
#   Support: IA-Arquiteto (0.85), IA-Developer (0.78)
# 
# 📋 Suggested Sequence:
#   1. IA-Auditor → Define security requirements
#   2. IA-Arquiteto → Design auth architecture  
#   3. IA-Developer → Implement with TDD
#   4. IA-QA → Security testing
#   5. IA-Ops → Deploy with monitoring
# 
# 💰 Estimated Cost: $0.45
# ⏱️  Estimated Time: 4 hours
# 
# ⚡ Execute now? [Y/n]
```

Type `Y` and watch the squad work! 🎉

### Example 2: With Context File
```bash
# Create a context file
cat > /tmp/checkout-requirements.md << 'EOF'
# Checkout Flow Requirements

## Business Context
- E-commerce platform for clothing
- Need to support credit card and PayPal
- Average order: $75
- Target: < 2 second checkout time

## Technical Context
- Spring Boot 3.2 backend
- React 18 frontend
- PostgreSQL database
- Existing shopping cart (working)

## Constraints
- Must be PCI-DSS compliant
- Budget: $500 infrastructure/month
- Timeline: 2 weeks
EOF

# Route with context
./scripts/orchestrator/route-problem.sh \
  --query="Design and implement checkout flow" \
  --context-file=/tmp/checkout-requirements.md

# Output:
# 🎯 Analysis Complete
# 
# Problem Type: feature_implementation
# Complexity: high
# Business Impact: critical
# 
# 🤖 Recommended Squad:
#   Primary: IA-Business-Analyst (confidence: 0.89)
#   Support: IA-Arquiteto (0.87), IA-Developer (0.82),
#            IA-Auditor (0.91), IA-Ops (0.75)
# 
# 📋 Multi-Phase Strategy Recommended:
#   
#   Phase 1: Discovery (1 day)
#     - IA-Business-Analyst: Define user stories
#     - IA-Designer: Checkout UI mockups
#   
#   Phase 2: Architecture (1 day)
#     - IA-Arquiteto: System design
#     - IA-Data-Architect: Payment data model
#     - IA-Auditor: PCI-DSS requirements
#   
#   Phase 3: Implementation (1 week)
#     - IA-Developer: Backend + Frontend
#     - IA-QA: Continuous testing
#   
#   Phase 4: Validation (2 days)
#     - IA-QA: Full test suite
#     - IA-Auditor: Security audit
#     - IA-Ops: Performance testing
#   
#   Phase 5: Deployment (1 day)
#     - IA-Ops: Production deployment
# 
# 💰 Total Estimated Cost: $12.50
# ⏱️  Total Estimated Time: 2 weeks
# 
# ⚡ Execute multi-phase strategy? [Y/n]
```

### Example 3: Manual IA Selection
```bash
# Activate specific IA directly
./scripts/orchestrator/activate-ia.sh ia-developer \
  --task="Refactor UserService class" \
  --context="450 lines, cyclomatic complexity 25, needs extraction"

# Output:
# 🤖 Activating: IA-Developer
# 📚 Loading mental models: Clean Code, Pragmatic Programmer
# 🎯 Applying principles: SRP, Clean Code
# 
# Analysis:
# - Class has 5 distinct responsibilities
# - Recommendation: Extract into separate services
# 
# Executing refactoring...
# ✅ Created 5 service classes
# ✅ Added 23 unit tests (87% coverage)
# ✅ Reduced complexity from 25 to avg 5
# 
# Duration: 1h 35m
# Cost: $0.08
# 
# Handoff to IA-QA? [Y/n]
```

---

## Understanding the Squad

### Squad Composition

BuildToValue v7 includes **11 specialized AI personas**:
```bash
# View squad status
./scripts/orchestrator/squad-status.sh

# Output:
# BuildToValue v7 - Squad Status
# ════════════════════════════════════════════════════
# 
# Strategy Squad (2 IAs):
#   ✅ IA-Product-Manager    [L3] - 89% confidence
#   ✅ IA-Business-Analyst   [L3] - 84% confidence
# 
# Design Squad (1 IA):
#   ✅ IA-Designer           [L3] - 88% confidence
# 
# Technical Squad (4 IAs):
#   ✅ IA-Arquiteto          [L4] - 89% confidence
#   ✅ IA-Developer          [L3] - 86% confidence
#   ✅ IA-QA-Engineer        [L3] - 87% confidence
#   ✅ IA-Auditor            [L5] - 92% confidence ⭐
# 
# Support Squad (4 IAs):
#   ✅ IA-Ops                [L4] - 89% confidence
#   ✅ IA-Data-Architect     [L3] - 83% confidence
#   ✅ IA-Integration        [L4] - 86% confidence
#   ✅ IA-Ethics-Guardian    [L5] - 91% confidence ⭐
# 
# ⭐ = Veto power (can block other IAs)
# [LX] = Autonomy level (1=low, 5=full)
```

### Key Personas to Know

**🎯 IA-Arquiteto** (Architect)
- **When to use**: System design, technology choices, patterns
- **Mental models**: Clean Architecture, DDD
- **Example**: "Design microservices architecture for order system"

**💻 IA-Developer** (Developer)
- **When to use**: Code implementation, refactoring, bug fixes
- **Mental models**: Clean Code, Pragmatic Programmer
- **Example**: "Implement checkout service with unit tests"

**🛡️ IA-Auditor** (Security)
- **When to use**: Security reviews, vulnerability scans, compliance
- **Mental models**: Web App Hacker's Handbook, OWASP
- **Example**: "Security review of authentication flow"
- **Special**: Can veto deployments (L5 autonomy)

**🎨 IA-Designer** (UX/UI)
- **When to use**: Interface design, user experience, accessibility
- **Mental models**: Don't Make Me Think
- **Example**: "Design checkout flow with mobile-first approach"

**🔧 IA-Ops** (DevOps)
- **When to use**: Infrastructure, deployment, monitoring
- **Mental models**: Phoenix Project, SRE
- **Example**: "Setup production infrastructure with auto-scaling"

### Autonomy Levels Explained

| Level | Description | Human Involvement |
|-------|-------------|-------------------|
| **L1** | Suggests only | Approve every action |
| **L2** | Limited execution | Notified of actions |
| **L3** | Moderate autonomy | Periodic review |
| **L4** | High autonomy | Exception-based review |
| **L5** | Full autonomy | Can veto others |
```bash
# View autonomy details
./scripts/orchestrator/autonomy-status.sh

# Adjust autonomy (if needed)
./scripts/orchestrator/set-autonomy.sh \
  --ia=ia-developer \
  --level=4 \
  --reason="Consistent high performance"
```

---

## Basic Workflows

### Workflow 1: New Feature Development
```bash
# 1. Define the feature
./scripts/orchestrator/route-problem.sh \
  "Implement user profile editing with photo upload"

# 2. Squad automatically determines:
#    - IA-Product-Manager: Define requirements
#    - IA-Designer: Design UI
#    - IA-Arquiteto: Architecture
#    - IA-Developer: Implementation
#    - IA-QA: Testing
#    - IA-Ops: Deployment

# 3. Monitor progress
./scripts/monitoring/active-tasks.sh

# 4. View results
./scripts/ledger/recent-decisions.sh --limit=5

# 5. Check quality
./scripts/gates-v7.sh --full
```

### Workflow 2: Bug Fix
```bash
# 1. Report the bug
./scripts/orchestrator/activate-ia.sh ia-developer \
  --task="Fix: Login fails with OAuth2 on mobile" \
  --context="Error: 'redirect_uri mismatch', only on iOS Safari"

# 2. IA-Developer analyzes and fixes
# 3. Automatically hands off to IA-QA
# 4. IA-Auditor reviews security implications

# 5. View the fix
./scripts/ledger/trace-decision.sh --id=DEC-2025-XXX
```

### Workflow 3: Security Review
```bash
# 1. Request security audit
./scripts/orchestrator/activate-ia.sh ia-auditor \
  --task="Security audit of payment processing" \
  --context="Stripe integration, stores card tokens"

# 2. IA-Auditor performs comprehensive review
# 3. Generates report with findings
# 4. Blocks deployment if critical issues found

# 5. View security report
cat .buildtovalue/reports/security-audit-latest.md
```

### Workflow 4: Architecture Decision
```bash
# 1. Present the problem
./scripts/orchestrator/route-problem.sh \
  "Should we use microservices or monolith for order system?"

# 2. Multiple IAs weigh in:
#    - IA-Arquiteto: Technical perspective
#    - IA-Developer: Implementation complexity
#    - IA-Ops: Operational overhead

# 3. Weighted voting or consensus

# 4. ADR automatically generated
ls docs/ADR/

# 5. View the decision
cat docs/ADR/ADR-XXX-order-system-architecture.md
```

---

## Next Steps

### Learn More

1. **📖 Read Documentation**
```bash
   # Core guides
   cat docs/ORCHESTRATION-GUIDE.md  # How to orchestrate
   cat docs/SQUAD-PERSONAS.md       # Understand each IA
   cat docs/ARCHITECTURE.md         # System architecture
```

2. **🎓 Complete Tutorials**
```bash
   # Interactive tutorials
   ./scripts/tutorials/01-basic-routing.sh
   ./scripts/tutorials/02-handoffs.sh
   ./scripts/tutorials/03-conflict-resolution.sh
   ./scripts/tutorials/04-autonomy-management.sh
```

3. **🔬 Experiment**
```bash
   # Try different scenarios
   ./scripts/orchestrator/route-problem.sh "Your problem here"
   
   # View what happened
   ./scripts/monitoring/squad-dashboard.sh
```

### Customize Your Squad
```bash
# 1. Adjust personas for your domain
nano .buildtovalue/squad/personas/ia-developer.yaml

# 2. Add domain-specific references
# Example: Add "Domain-Driven Design in Practice" for fintech

# 3. Update activation matrix
nano .buildtovalue/orchestration/activation-matrix.yaml

# 4. Test your changes
./scripts/squad/validate-personas.sh
./scripts/squad/reload-personas.sh
```

### Join the Community

- **Discord**: https://discord.gg/buildtovalue
- **GitHub Discussions**: https://github.com/buildtovalue/v7/discussions
- **Weekly Office Hours**: Every Friday 3pm UTC on Discord

### Get Certified
```bash
# Work towards certification
./scripts/certification/check-status.sh

# Bronze: Squad + gates 80%
# Silver: Squad + Auto-RAG + observability
# Gold: Learning + tracing + contributions
```

---

## Troubleshooting Installation

### Docker Services Not Starting
```bash
# Check Docker is running
docker ps

# If not running:
sudo systemctl start docker

# Check logs
docker-compose -f docker/docker-compose-v7.yml logs

# Restart services
docker-compose -f docker/docker-compose-v7.yml restart
```

### API Key Issues
```bash
# Test OpenAI connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return list of models
# If error: check your API key is correct and has credits
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose -f docker/docker-compose-v7.yml ps postgres

# Check connection
docker exec -it buildtovalue-postgres psql -U btv_user -d buildtovalue

# If connection works but app doesn't:
# Verify .env.dev has correct POSTGRES_HOST (should be 'localhost' for local)
```

### Port Conflicts
```bash
# Check if ports are already in use
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis
sudo lsof -i :8080  # Application
sudo lsof -i :3000  # Grafana

# Change ports in docker-compose-v7.yml if needed
nano docker/docker-compose-v7.yml
```

### Low Disk Space
```bash
# Check disk usage
df -h

# Clean Docker (if needed)
docker system prune -a --volumes

# Warning: This removes all unused Docker data
```

### Memory Issues
```bash
# Check available memory
free -h

# If < 8GB available, close other applications
# Or increase Docker memory limit:
# Docker Desktop → Settings → Resources → Memory → 8GB
```

---

## Common Questions

**Q: Which AI provider should I use?**
A: Start with OpenAI GPT-4 for best results. You can add Anthropic Claude or Google Gemini later for comparison.

**Q: How much does it cost to run?**
A: Locally: $0 (just your API calls). Typical costs: $0.05-$0.15 per decision. A full project might be $10-$50 in API costs.

**Q: Can I use this for production projects?**
A: Yes! BuildToValue v7 is production-ready. Many teams use it for real products. Start with Lite foundation, scale to Standard/Enterprise as needed.

**Q: Do I need to know AI/ML?**
A: No! You just describe problems in natural language. The squad handles the AI orchestration automatically.

**Q: Can I customize the AI personas?**
A: Absolutely! Edit `.buildtovalue/squad/personas/*.yaml` to adjust mental models, autonomy levels, and activation triggers for your domain.

**Q: What if the AI makes a mistake?**
A: You can always override decisions manually. The system learns from your corrections. Human-in-the-loop is built-in.

**Q: How do I upgrade from v6?**
A: See [MIGRATION-v6-to-v7.md](./MIGRATION-v6-to-v7.md) for step-by-step upgrade guide.

---

## Getting Help

### 1. Check Documentation
```bash
# Search docs
grep -r "your question" docs/

# View specific guide
cat docs/TROUBLESHOOTING.md
```

### 2. Run Diagnostics
```bash
./scripts/troubleshooting/health-check.sh
./scripts/troubleshooting/diagnostic-report.sh
```

### 3. Community Support
- **Discord**: Fastest response, community + maintainers
- **GitHub Issues**: Bug reports and feature requests
- **Email**: support@buildtovalue.com (paid support)

### 4. Emergency
```bash
# Generate support bundle
./scripts/troubleshooting/generate-support-bundle.sh

# This creates: buildtovalue-support-bundle-TIMESTAMP.zip
# Share this with support for faster resolution
```

---

## What's Next?

Now that you have BuildToValue v7 running:

1. ✅ **Complete your first feature** using the squad
2. ✅ **Customize personas** for your domain
3. ✅ **Integrate with your CI/CD** pipeline
4. ✅ **Monitor squad performance** and optimize
5. ✅ **Share your experience** with the community

**Welcome to the future of AI-assisted development!** 🚀

---

**Document Version:** 7.0.0  
**Last Updated:** 2025-01-20  
**Maintained By:** BuildToValue Onboarding Team  

© 2025 BuildToValue | [Full Documentation](./README.md) | [GitHub](https://github.com/buildtovalue/v7)
