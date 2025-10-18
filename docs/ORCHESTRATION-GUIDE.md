# 🎭 BuildToValue v7.0 - Orchestration Guide

Complete guide for orchestrating the AI squad effectively.

## 📑 Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Smart Routing System](#smart-routing-system)
- [Handoff Protocols](#handoff-protocols)
- [Conflict Resolution](#conflict-resolution)
- [Autonomy Management](#autonomy-management)
- [Communication Patterns](#communication-patterns)
- [Decision Tracking](#decision-tracking)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Advanced Techniques](#advanced-techniques)

---

## Overview

### What is Orchestration?
Orchestration is the process of coordinating multiple AI personas to work together efficiently on complex problems. As a Prompt Engineer, you are the conductor of this AI orchestra.

### Your Role as Orchestrator
```yaml
yamlorchestrator_responsibilities:
  strategic:
    - "Define project vision and constraints"
    - "Approve high-impact decisions"
    - "Resolve escalated conflicts"
    - "Adjust squad composition as needed"
  
  tactical:
    - "Route problems to appropriate IAs"
    - "Monitor handoff quality"
    - "Ensure communication clarity"
    - "Track performance metrics"
  
  operational:
    - "Trigger IA activations"
    - "Facilitate inter-IA consultations"
    - "Capture lessons learned"
    - "Maintain mental model alignment"
```

### Orchestration Modes
BuildToValue v7 supports three orchestration modes:

| Mode      | Description                                | Use Case                       | Automation Level |
|-----------|--------------------------------------------|--------------------------------|------------------|
| Manual    | You explicitly activate each IA            | Learning, complex problems     | 0%               |
| Assisted  | System suggests IAs, you approve           | Standard development           | 50%              |
| Autonomous| System routes automatically                | Routine tasks, proven patterns | 90%              |

```bash
# Set orchestration mode
./scripts/orchestrator/set-mode.sh --mode=assisted

# Check current mode
./scripts/orchestrator/get-mode.sh
# Output: Current mode: assisted (confidence threshold: 0.75)
```

---

## Core Concepts

### 1. Activation Matrix
The Activation Matrix determines which IA should handle which type of problem.

```yaml
yaml# .buildtovalue/orchestration/activation-matrix.yaml

activation_rules:
  
  problem_type_mapping:
    product_strategy:
      primary: "ia-product-manager"
      support: ["ia-business-analyst"]
      confidence_threshold: 0.75
    
    business_rules:
      primary: "ia-business-analyst"
      support: ["ia-arquiteto", "ia-developer"]
      confidence_threshold: 0.75
    
    architecture:
      primary: "ia-arquiteto"
      support: ["ia-developer", "ia-ops"]
      confidence_threshold: 0.80
      requires_consensus: true
    
    implementation:
      primary: "ia-developer"
      support: ["ia-qa", "ia-arquiteto"]
      confidence_threshold: 0.75
      parallel_review: ["ia-auditor"]
    
    security:
      primary: "ia-auditor"
      support: ["ia-arquiteto", "ia-developer"]
      confidence_threshold: 0.85
      veto_power: true
    
    ui_design:
      primary: "ia-designer"
      support: ["ia-product-manager", "ia-developer"]
      confidence_threshold: 0.75
    
    infrastructure:
      primary: "ia-ops"
      support: ["ia-arquiteto", "ia-developer"]
      confidence_threshold: 0.80
    
    data_modeling:
      primary: "ia-data-architect"
      support: ["ia-business-analyst", "ia-arquiteto"]
      confidence_threshold: 0.75
    
    integration:
      primary: "ia-integration-specialist"
      support: ["ia-arquiteto", "ia-ops"]
      confidence_threshold: 0.80
    
    ethics_review:
      primary: "ia-ethics-guardian"
      support: []
      confidence_threshold: 0.85
      veto_power: true

  semantic_triggers:
    # Keywords that trigger specific IAs
    keywords:
      product: ["vision", "roadmap", "market", "strategy", "customer"]
      business: ["rules", "validation", "process", "workflow", "domain"]
      architecture: ["design", "scalability", "patterns", "technology"]
      code: ["implement", "refactor", "bug", "optimize", "test"]
      security: ["vulnerability", "encryption", "authentication", "compliance"]
      design: ["ui", "ux", "interface", "mockup", "usability"]
      ops: ["deploy", "infrastructure", "monitor", "scaling", "incident"]
      data: ["database", "privacy", "pii", "gdpr", "retention"]
      integration: ["api", "sync", "cross-platform", "interoperability"]
      ethics: ["bias", "fairness", "privacy", "harm", "discrimination"]
```

### 2. Confidence Scoring
Each routing decision has a confidence score (0.0 to 1.0) indicating how certain the system is about the choice.

```python
def calculate_routing_confidence(problem, ia):
    """
    Calculate confidence that IA should handle problem
    
    Factors:
    - Historical success rate (40%)
    - Mental model match (35%)
    - Current autonomy level (15%)
    - Recent performance (10%)
    """
    
    weights = {
        'historical': 0.40,
        'mental_model': 0.35,
        'autonomy': 0.15,
        'recent': 0.10
    }
    
    # Historical success
    historical = get_success_rate(
        ia=ia,
        problem_type=classify(problem),
        lookback_days=90
    )
    
    # Mental model match
    mental_model_score = semantic_similarity(
        problem_embedding=embed(problem),
        ia_references=ia.mental_models.primary_reference
    )
    
    # Autonomy (normalized 1-5 → 0-1)
    autonomy = ia.autonomy.current_level / 5.0
    
    # Recent performance
    recent = get_recent_success_rate(ia, last_n=10)
    
    confidence = (
        weights['historical'] * historical +
        weights['mental_model'] * mental_model_score +
        weights['autonomy'] * autonomy +
        weights['recent'] * recent
    )
    
    return min(1.0, max(0.0, confidence))
```

**Confidence Thresholds**

- ≥ 0.85: High confidence - autonomous execution
- 0.75 - 0.84: Medium confidence - execute with notification
- 0.60 - 0.74: Low confidence - request human review
- < 0.60: Very low - escalate to human immediately

### 3. Context Preservation
Context is critical for effective handoffs. Use the CIIF Protocol.

```yaml
yamlciif_protocol:
  C_context:
    description: "Current state and background"
    includes:
      - "What stage of development (discovery, design, implementation, testing)"
      - "Previous decisions made"
      - "Constraints (technical, business, budget, timeline)"
      - "Related work or dependencies"
  
  I_information:
    description: "Concrete data and artifacts"
    includes:
      - "Documents, diagrams, code, tests"
      - "Data models, API specs, configurations"
      - "Links to external resources"
      - "Checksums for verification"
  
  I_intention:
    description: "Desired outcome and success criteria"
    includes:
      - "What we're trying to achieve"
      - "Why this matters (business value)"
      - "How we'll know it's successful"
      - "Monitoring/validation checkpoints"
  
  F_format:
    description: "Expected deliverable format"
    includes:
      - "Type of output (code, document, diagram, ADR)"
      - "Templates to use"
      - "Quality standards"
      - "Review process"
```

---

## Smart Routing System

### How Smart Routing Works
```
┌─────────────────────────────────────────────────────────┐
│                    Problem Submitted                     │
│            "Implement OAuth2 authentication"             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Semantic Analysis    │
         │  - Extract keywords   │
         │  - Classify type      │
         │  - Assess complexity  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  RAG Search           │
         │  - Find similar cases │
         │  - Extract patterns   │
         │  - Get success rate   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Confidence Calc      │
         │  - Per IA scoring     │
         │  - Rank candidates    │
         │  - Check thresholds   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Conflict Prediction  │
         │  - Check history      │
         │  - Assess risk        │
         │  - Suggest mediator   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Cost Optimization    │
         │  - Estimate cost      │
         │  - Check budget       │
         │  - Consider cheaper   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Ethics Check         │
         │  - IA-Ethics review   │
         │  - Flag concerns      │
         │  - Apply constraints  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Final Decision       │
         │  Primary: IA-Auditor  │
         │  Support: Arquiteto   │
         │  Confidence: 0.92     │
         └───────────────────────┘
```

### Manual Routing
When you know exactly which IA should handle a problem:

```bash
# Basic activation
./scripts/orchestrator/activate-ia.sh ia-developer \
  --task="Refactor UserService class" \
  --context="Legacy code, needs testing"

# With full context
./scripts/orchestrator/activate-ia.sh ia-arquiteto \
  --task="Design microservices architecture" \
  --context-file=./docs/requirements.md \
  --urgency=high \
  --budget=medium

# Multiple IAs (parallel)
./scripts/orchestrator/activate-squad.sh \
  --primary=ia-developer \
  --support=ia-qa,ia-auditor \
  --task="Implement payment processing"
```

### Automatic Routing
Let the system decide based on problem analysis:

```bash
# Simple query
./scripts/orchestrator/route-problem.sh \
  "How should we implement user authentication?"

# Output:
# 🎯 Analysis Complete
# 
# Problem Type: security_implementation
# Complexity: high
# Estimated Duration: 2-3 days
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

With detailed context:

```bash
# From JSON context
./scripts/orchestrator/route-problem.sh \
  --query="Optimize database queries" \
  --context='{
    "domain": "e-commerce",
    "current_performance": "P95 2.5s",
    "target_performance": "P95 < 500ms",
    "budget": "high",
    "urgency": "critical"
  }'

# From file
./scripts/orchestrator/route-problem.sh \
  --query="Design checkout flow" \
  --context-file=./docs/checkout-requirements.md \
  --mode=assisted
```

### Routing with Constraints

```bash
# Only consider specific IAs
./scripts/orchestrator/route-problem.sh \
  "Refactor legacy code" \
  --ias=ia-developer,ia-arquiteto

# Exclude certain IAs
./scripts/orchestrator/route-problem.sh \
  "Quick bug fix" \
  --exclude=ia-product-manager,ia-designer

# Force minimum confidence
./scripts/orchestrator/route-problem.sh \
  "Deploy to production" \
  --min-confidence=0.90

# Set cost limit
./scripts/orchestrator/route-problem.sh \
  "Generate API documentation" \
  --max-cost=0.10
```

### Viewing Routing Decisions

```bash
# View last routing decision
./scripts/orchestrator/show-last-routing.sh

# View routing history
./scripts/orchestrator/routing-history.sh --last=10

# Analyze routing accuracy
./scripts/orchestrator/routing-accuracy.sh --period=last-month
```

---

## Handoff Protocols

### Standard Handoff Process
```yaml
yamlhandoff_process:
  
  step_1_preparation:
    action: "Source IA prepares handoff package"
    artifacts:
      - "Completed work"
      - "Context document (CIIF format)"
      - "Known issues or blockers"
      - "Recommendations for next steps"
  
  step_2_notification:
    action: "System notifies target IA"
    includes:
      - "Source IA identity"
      - "Task description"
      - "Priority level"
      - "Estimated effort"
  
  step_3_context_transfer:
    action: "Target IA reviews context"
    validation:
      - "All artifacts present"
      - "Context is clear"
      - "Success criteria defined"
      - "No missing information"
  
  step_4_acknowledgment:
    action: "Target IA acknowledges receipt"
    confirms:
      - "Understanding of task"
      - "Acceptance of success criteria"
      - "No blockers to proceeding"
  
  step_5_execution:
    action: "Target IA begins work"
    tracking:
      - "Start timestamp"
      - "Progress updates"
      - "Issue discovery"
  
  step_6_completion:
    action: "Target IA delivers results"
    includes:
      - "Completed artifacts"
      - "Updated context"
      - "Next steps"
```

### Executing a Handoff

```bash
# Manual handoff
./scripts/orchestrator/handoff.sh \
  --from=ia-arquiteto \
  --to=ia-developer \
  --artifacts="docs/ADR-005.md,diagrams/architecture.svg" \
  --context="Microservices architecture approved, implement Order service"

# With CIIF template
./scripts/orchestrator/handoff.sh \
  --from=ia-business-analyst \
  --to=ia-developer \
  --ciif-file=./handoffs/checkout-flow.yaml

# Batch handoff (one to many)
./scripts/orchestrator/handoff.sh \
  --from=ia-arquiteto \
  --to=ia-developer,ia-ops,ia-auditor \
  --broadcast \
  --artifacts="docs/system-design.md"
```

### CIIF Template Example

```yaml
yaml# handoffs/checkout-flow.yaml

handoff:
  from: "ia-business-analyst"
  to: "ia-developer"
  timestamp: "2025-01-20T14:30:00Z"
  
  context:
    stage: "implementation"
    previous_decisions:
      - id: "DEC-2025-042"
        decision: "Use Stripe for payment processing"
        rationale: "Best API, lowest fees, excellent documentation"
    
    constraints:
      - "Must work with existing shopping cart"
      - "PCI-DSS compliance required"
      - "Support credit card and PayPal"
      - "P95 latency < 2 seconds"
    
    related_work:
      - "Shopping cart implemented (PR #234)"
      - "User authentication complete (PR #156)"
  
  information:
    artifacts:
      - type: "user_stories"
        location: "docs/user-stories/checkout.md"
        checksum: "sha256:a3f5b2c8..."
      
      - type: "domain_model"
        location: "docs/domain/checkout-context.md"
        checksum: "sha256:d7e9a1f3..."
      
      - type: "acceptance_criteria"
        location: "docs/acceptance/checkout-criteria.md"
        checksum: "sha256:b8c3d4e5..."
    
    business_rules:
      - "Minimum order: $5"
      - "Maximum order: $5000"
      - "Tax calculation: based on ship-to address"
      - "Discounts applied before tax"
    
    examples:
      - scenario: "Successful checkout"
        given: "Cart with 3 items totaling $50"
        when: "User completes checkout with credit card"
        then: "Order created, payment authorized, email sent"
      
      - scenario: "Payment declined"
        given: "Cart with items totaling $100"
        when: "Credit card declined"
        then: "Show error, allow retry, don't create order"
  
  intention:
    objective: |
      Implement checkout flow that allows users to complete purchase
      with credit card or PayPal, handling success and error cases gracefully.
    
    business_value: |
      Enable revenue generation. Each 1% improvement in checkout completion
      = $50k annual revenue increase based on current traffic.
    
    success_criteria:
      functional:
        - "User can complete checkout with valid payment"
        - "Declined payments handled gracefully"
        - "Order confirmation email sent"
        - "Inventory updated after purchase"
      
      non_functional:
        - "P95 latency < 2 seconds"
        - "PCI-DSS compliant (no card data stored)"
        - "99.9% success rate for valid payments"
      
      testing:
        - "Unit tests for all payment scenarios"
        - "Integration tests with Stripe test mode"
        - "Manual test with real card in staging"
    
    monitoring_checkpoints:
      - "After unit tests: verify logic correct"
      - "After integration: verify Stripe integration works"
      - "Before production: IA-Auditor security review"
  
  format:
    expected_output:
      - "CheckoutService.java with complete logic"
      - "Unit tests (>80% coverage)"
      - "Integration tests"
      - "API documentation (OpenAPI)"
      - "README with setup instructions"
    
    quality_standards:
      - "Follow Clean Code principles"
      - "No hardcoded secrets"
      - "All errors use RFC 7807 format"
      - "Logging for all payment operations"
    
    review_process:
      - "Self-review before handoff to IA-QA"
      - "IA-QA functional testing"
      - "IA-Auditor security review"
      - "IA-Ops deployment verification"
```

### Monitoring Handoffs

```bash
# View active handoffs
./scripts/orchestrator/active-handoffs.sh

# Track specific handoff
./scripts/orchestrator/track-handoff.sh HANDOFF-2025-015

# Handoff metrics
./scripts/orchestrator/handoff-metrics.sh --period=last-sprint
```

### Handoff Best Practices

```yaml
yamlbest_practices:
  
  clear_context:
    do:
      - "Use CIIF format consistently"
      - "Include concrete examples"
      - "Link to related work"
      - "State assumptions explicitly"
    
    dont:
      - "Assume target IA has implicit knowledge"
      - "Use vague terms like 'should be good'"
      - "Skip success criteria"
      - "Forget to mention blockers"
  
  artifact_quality:
    do:
      - "Verify artifacts are complete"
      - "Include checksums for verification"
      - "Organize files logically"
      - "Document any known issues"
    
    dont:
      - "Hand off work-in-progress without explanation"
      - "Mix multiple concerns in one artifact"
      - "Forget to version artifacts"
  
  timing:
    do:
      - "Hand off at logical boundaries"
      - "Allow buffer time for review"
      - "Notify in advance if complex"
    
    dont:
      - "Hand off at end of day (no time to clarify)"
      - "Rush handoffs due to deadline pressure"
      - "Hand off multiple complex items simultaneously"
```

---

## Conflict Resolution

### Types of Conflicts

```yaml
yamlconflict_types:
  
  technical_disagreement:
    example: "IA-Arquiteto suggests microservices, IA-Developer prefers monolith"
    resolution: "Weighted voting based on technical expertise"
    arbiter: "ia-arquiteto"
  
  business_priority:
    example: "IA-Product-Manager wants feature X, IA-Business-Analyst says Y is more important"
    resolution: "Business impact analysis"
    arbiter: "ia-product-manager"
  
  security_vs_usability:
    example: "IA-Auditor requires complex password, IA-Designer says too hard for users"
    resolution: "Find middle ground with MFA"
    arbiter: "ia-auditor" # Security wins by default
  
  performance_vs_cost:
    example: "IA-Ops wants more servers, IA-FinOps says too expensive"
    resolution: "Cost-benefit analysis"
    arbiter: "human" # Budget decisions escalate
  
  timeline_vs_quality:
    example: "IA-QA needs more time, IA-Product-Manager wants to ship"
    resolution: "Error budget approach"
    arbiter: "ia-product-manager" # With IA-QA input
```

### Resolution Levels

```yaml
yamlresolution_levels:
  
  level_1_direct_negotiation:
    duration: "30 minutes"
    process: |
      1. Both IAs present their positions
      2. Each provides rationale with references
      3. Attempt to find common ground
      4. Document agreement or escalate
    
    success_rate: 60%
    
    example: |
      Conflict: Database choice (PostgreSQL vs MongoDB)
      IA-Arquiteto: "PostgreSQL for ACID transactions"
      IA-Developer: "MongoDB for schema flexibility"
      Resolution: "PostgreSQL with JSONB columns for flexibility"
  
  level_2_weighted_voting:
    duration: "15 minutes"
    process: |
      1. Identify all stakeholder IAs
      2. Each votes with confidence score
      3. Weight by expertise in this domain
      4. Calculate weighted result
      5. If >80% agreement, accept; else escalate
    
    success_rate: 85%
    
    example: |
      Conflict: API design approach (REST vs GraphQL)
      Votes:
        ia-arquiteto: REST (confidence: 0.85, weight: 0.5) = 0.425
        ia-developer: GraphQL (confidence: 0.75, weight: 0.3) = 0.225
        ia-integration: REST (confidence: 0.80, weight: 0.2) = 0.160
      
      Weighted sum: REST = 0.585, GraphQL = 0.225
      Result: REST wins (71% agreement)
  
  level_3_expert_arbitration:
    duration: "1 hour"
    process: |
      1. Identify most qualified IA for this domain
      2. Present both arguments to arbiter
      3. Arbiter researches and deliberates
      4. Arbiter makes final decision with rationale
      5. Document decision as ADR
    
    success_rate: 95%
    
    example: |
      Conflict: Security approach (session vs JWT)
      Arbiter: IA-Auditor (security expert)
      Research: Reviews OWASP guidelines, attack vectors
      Decision: "JWT with short expiry + refresh tokens"
      Rationale: "Better for distributed systems, manageable risk"
      ADR: docs/ADR/ADR-023-authentication-tokens.md
  
  level_4_human_escalation:
    duration: "Variable"
    process: |
      1. Document full context of conflict
      2. Present all IA arguments
      3. Include recommendation
      4. Human (Prompt Engineer) decides
      5. Capture rationale for future learning
    
    success_rate: 100%
    
    triggers:
      - "Conflict persists after Level 3"
      - "High business impact (>$10k)"
      - "Ethical concerns"
      - "Compliance uncertainty"
```

### Executing Conflict Resolution

```bash
# Detect conflict
./scripts/orchestrator/detect-conflict.sh \
  --ias=ia-arquiteto,ia-developer \
  --topic="microservices_vs_monolith"

# Manual resolution trigger
./scripts/orchestrator/resolve-conflict.sh \
  --conflict-id=CONF-2025-008 \
  --method=weighted_voting

# View conflict history
./scripts/orchestrator/conflict-history.sh --period=last-month

# Conflict analytics
./scripts/orchestrator/conflict-analytics.sh
```

### Conflict Prevention

```yaml
yamlprevention_strategies:
  
  early_alignment:
    practice: "Involve relevant IAs early in decision-making"
    example: |
      Before deciding on architecture:
      1. IA-Business-Analyst presents requirements
      2. IA-Arquiteto proposes options
      3. IA-Developer assesses feasibility
      4. IA-Ops evaluates operational impact
      5. Consensus before commitment
  
  clear_decision_rights:
    practice: "Define who has final say in each domain"
    example: |
      Decision Rights Matrix:
      - Security: IA-Auditor (can veto)
      - Architecture: IA-Arquiteto (with input from others)
      - User Experience: IA-Designer (with product validation)
      - Deployment: IA-Ops (operational concerns)
  
  documented_principles:
    practice: "Reference shared mental models and principles"
    example: |
      When disagreeing, cite principles:
      "Per Clean Architecture (Chapter 17), dependencies should
       point inward, so we should..."
  
  conflict_prediction:
    practice: "Use ML to predict conflicts before they happen"
    example: |
      System detects:
      - IA-Auditor and IA-Developer have conflicted 3x on similar issues
      - Pre-emptively involves IA-Arquiteto as mediator
      - Schedules alignment session before work starts
```

---

## Autonomy Management

### Understanding Autonomy Levels

```yaml
yamlautonomy_levels:
  
  level_1_suggestion_only:
    description: "IA suggests, human approves every action"
    use_cases:
      - "New IA being trained"
      - "Critical production systems"
      - "High-risk decisions"
    
    workflow: |
      1. IA analyzes problem
      2. IA proposes solution
      3. Human reviews and approves
      4. IA executes approved solution
      5. Human validates result
    
    overhead: "Very high (5-10 minutes per decision)"
    error_risk: "Very low"
  
  level_2_limited_execution:
    description: "IA executes simple tasks, notifies human"
    use_cases:
      - "Junior-level tasks"
      - "Well-understood patterns"
      - "Low-risk operations"
    
    workflow: |
      1. IA analyzes problem
      2. IA executes if simple (confidence > 0.8)
      3. Human notified of action taken
      4. Human can rollback if needed
    
    overhead: "Medium (1-2 minutes per decision)"
    error_risk: "Low"
  
  level_3_moderate_autonomy:
    description: "IA decides and acts, periodic human review"
    use_cases:
      - "Standard development tasks"
      - "Mid-level complexity"
      - "Known problem domains"
    
    workflow: |
      1. IA analyzes, decides, and executes
      2. Human reviews batch of decisions daily/weekly
      3. Human provides feedback for learning
      4. Autonomy adjusted based on performance
    
    overhead: "Low (5-10 minutes daily review)"
    error_risk: "Medium"
  
  level_4_high_autonomy:
    description: "IA fully autonomous, human involved only on exceptions"
    use_cases:
      - "Senior-level tasks"
      - "Proven track record (>90% success)"
      - "Rapid iteration needed"
    
    workflow: |
      1. IA handles end-to-end
      2. Human alerted only if:
         - Confidence < threshold
         - Cost > budget
         - Error encountered
      3. Human reviews metrics weekly
    
    overhead: "Very low (30 minutes weekly)"
    error_risk: "Medium-High"
  
  level_5_full_autonomy:
    description: "IA has veto power, can block other IAs"
    use_cases:
      - "Security (IA-Auditor)"
      - "Ethics (IA-Ethics-Guardian)"
      - "Proven expertise domains"
    
    workflow: |
      1. IA operates independently
      2. Can override other IAs' decisions
      3. Human informed of vetoes
      4. Human can override only with explicit approval
    
    overhead: "Minimal (passive monitoring)"
    error_risk: "Low (high expertise + veto power)"
```

### Adjusting Autonomy Levels

```bash
# View current autonomy levels
./scripts/orchestrator/autonomy-status.sh

# Manually adjust autonomy
./scripts/orchestrator/set-autonomy.sh \
  --ia=ia-developer \
  --level=4 \
  --reason="Consistent high performance over 20 tasks"

# Automatic adjustment based on performance
./scripts/orchestrator/auto-adjust-autonomy.sh

# View autonomy history
./scripts/orchestrator/autonomy-history.sh --ia=ia-developer
```

### Autonomy Rules

```yaml
yamlautonomy_rules:
  
  increase_triggers:
    consecutive_success:
      condition: "10+ successful tasks with confidence > 0.85"
      action: "Increase by 1 level (max L4, L5 requires manual)"
    
    zero_human_overrides:
      condition: "30 days without human override"
      action: "Increase by 1 level"
    
    exceptional_performance:
      condition: "Success rate > 95% over 50 tasks"
      action: "Increase by 1 level"
  
  decrease_triggers:
    consecutive_failures:
      condition: "3+ failures in last 10 tasks"
      action: "Decrease by 1 level (min L1)"
    
    human_override:
      condition: "Human overrides decision"
      action: "Decrease by 1 level immediately"
    
    low_confidence:
      condition: "Average confidence < 0.60 over 10 tasks"
      action: "Decrease by 1 level"
    
    critical_error:
      condition: "Error causing production incident"
      action: "Decrease to L1 immediately"
  
  special_rules:
    security_ias:
      rule: "IA-Auditor and IA-Ethics-Guardian start at L5"
      rationale: "Security and ethics are non-negotiable"
    
    new_ias:
      rule: "New IAs start at L1 or L2"
      rationale: "Build trust through demonstrated performance"
    
    domain_specific:
      rule: "Autonomy can vary by task type"
      example: "IA-Developer L4 for backend, L2 for frontend (less experience)"
```

### Autonomy Best Practices

```yaml
yamlbest_practices:
  
  gradual_increase:
    do: "Increase autonomy incrementally based on performance"
    dont: "Jump from L1 to L4 without proven track record"
  
  domain_awareness:
    do: "Consider IA expertise in specific domains"
    example: "IA-Developer might be L4 in Java but L2 in Python"
  
  safety_nets:
    do: "Maintain monitoring even at high autonomy"
    tools:
      - "Automated alerts for anomalies"
      - "Periodic human review"
      - "Rollback mechanisms"
  
  transparency:
    do: "Communicate autonomy changes to team"
    format: |
      "IA-Developer promoted to L4 autonomy in backend tasks
       due to 15 consecutive successful implementations.
       Will continue L3 for frontend work."
  
  reversibility:
    do: "Be willing to decrease autonomy if performance degrades"
    mindset: "Autonomy is earned and maintained, not permanent"
```

---

## Communication Patterns

### Inter-IA Communication

```yaml
yamlcommunication_protocols:
  
  consultation:
    description: "IA seeks expert opinion from another IA"
    when_to_use:
      - "Uncertain about approach in another's domain"
      - "Need specialized knowledge"
      - "Want second opinion"
    
    format: |
      Consultation Request:
      From: {requesting_ia}
      To: {expert_ia}
      Question: {specific_question}
      Context: {relevant_background}
      Urgency: {low|medium|high}
    
    example: |
      From: ia-developer
      To: ia-arquiteto
      Question: "Should I use Observer or Mediator pattern for this event system?"
      Context: "Need to notify 5+ components when order status changes"
      Urgency: medium
      
      Response from ia-arquiteto:
      "Use Observer pattern. Martin Fowler's EAA Patterns recommends this
       for one-to-many notification. Mediator is overkill for your case.
       See: Gang of Four Observer pattern, page 293."
  
  alert:
    description: "IA notifies others of important issue"
    when_to_use:
      - "Problem detected that affects others"
      - "Violation of principles"
      - "Blocker discovered"
    
    severity_levels:
      critical: "Immediate action required, blocks progress"
      high: "Important issue, should address today"
      medium: "Notable concern, address this sprint"
      low: "Minor issue, address when convenient"
    
    format: |
      Alert:
      From: {alerting_ia}
      To: {affected_ias}
      Severity: {critical|high|medium|low}
      Issue: {brief_description}
      Impact: {how_it_affects_work}
      Recommendation: {suggested_action}
    
    example: |
      From: ia-auditor
      To: ia-developer, ia-arquiteto
      Severity: CRITICAL
      Issue: "SQL injection vulnerability in UserRepository.findByUsername()"
      Impact: "Entire user database at risk of unauthorized access"
      Recommendation: "Stop work immediately. Use parameterized query:
                       PreparedStatement ps = conn.prepareStatement(
                         'SELECT * FROM users WHERE username = ?'
                       )"
  
  suggestion:
    description: "IA proposes improvement to another's work"
    when_to_use:
      - "See opportunity for optimization"
      - "Notice pattern that could be improved"
      - "Have alternative approach"
    
    format: |
      Suggestion:
      From: {suggesting_ia}
      To: {recipient_ia}
      Current_Approach: {what_they_did}
      Suggested_Approach: {alternative}
      Rationale: {why_it's_better}
      References: {supporting_materials}
      Priority: {nice_to_have|recommended|important}
    
    example: |
      From: ia-arquiteto
      To: ia-developer
      Current_Approach: "Direct database access from controllers"
      Suggested_Approach: "Introduce Repository pattern"
      Rationale: "Better testability, cleaner separation of concerns,
                  easier to swap data sources. Clean Architecture Ch 22."
      References: "Patterns of EAA by Fowler, Repository pattern"
      Priority: recommended
      
      Response from ia-developer:
      "Accepted. Will refactor in next PR. Thanks for the suggestion."
  
  broadcast:
    description: "IA shares information with entire squad"
    when_to_use:
      - "Decision that affects everyone"
      - "New constraint or requirement"
      - "Important discovery"
    
    format: |
      Broadcast:
      From: {broadcasting_ia}
      Subject: {brief_title}
      Message: {detailed_information}
      Action_Required: {what_squad_should_do}
      Deadline: {if_applicable}
    
    example: |
      From: ia-ops
      To: ALL_SQUAD
      Subject: "Database maintenance window scheduled"
      Message: "PostgreSQL will be upgraded from 14 to 15 on
                Saturday 2025-01-25 02:00-06:00 UTC.
                Expect 15-minute downtime during cutover."
      Action_Required: "Ensure your code is compatible with PG15.
                        Review: https://docs.postgresql.org/15/release-15.html"
      Deadline: "2025-01-24 (day before maintenance)"
```

### Executing Communication

```bash
# Consultation
./scripts/orchestrator/consult.sh \
  --from=ia-developer \
  --to=ia-arquiteto \
  --question="Best caching strategy for product catalog?" \
  --context="10k products, updated daily, read-heavy"

# Alert
./scripts/orchestrator/alert.sh \
  --from=ia-auditor \
  --to=ia-developer,ia-ops \
  --severity=high \
  --issue="Missing rate limiting on login endpoint" \
  --impact="Vulnerable to brute force attacks"

# Suggestion
./scripts/orchestrator/suggest.sh \
  --from=ia-arquiteto \
  --to=ia-developer \
  --current="Using multiple if-else for order status" \
  --suggested="Use State pattern for cleaner status transitions" \
  --priority=recommended

# Broadcast
./scripts/orchestrator/broadcast.sh \
  --from=ia-ops \
  --subject="New deployment process" \
  --message="Now using canary deployments: 10% → 50% → 100%" \
  --action="Update your deployment scripts"

# View communication history
./scripts/orchestrator/communication-log.sh --last=20

# Communication analytics
./scripts/orchestrator/communication-stats.sh
```

---

## Decision Tracking

### Ledger Structure

```yaml
yamldecision_ledger:
  location: ".buildtovalue/ledger/decisions/"
  format: "JSON Lines (one JSON object per line)"
  retention: "Indefinite (append-only)"
  
  entry_schema:
    id: "DEC-{YYYY}-{NNN}"
    timestamp: "ISO 8601"
    problem: "Original problem description"
    problem_type: "Classification"
    context: "Additional context object"
    
    routing:
      method: "automatic | ml | human"
      primary_ia: "Selected IA"
      support_ias: ["Supporting IAs"]
      confidence: "0.0-1.0"
      estimated_cost: "USD"
      estimated_duration: "seconds"
    
    decision:
      chosen_option: "What was decided"
      alternatives: ["Other options considered"]
      rationale: "Why this option"
      references: ["Mental model references cited"]
    
    execution:
      start_time: "ISO 8601"
      end_time: "ISO 8601"
      actual_cost: "USD"
      success: "boolean"
      confidence_actual: "0.0-1.0"
      human_intervention: "boolean"
    
    outcome:
      artifacts_created: ["List of deliverables"]
      next_steps: ["Follow-up actions"]
      lessons_learned: "What we learned"
      tags: ["Categorization tags"]
```

### Querying the Ledger

```bash
# Recent decisions
./scripts/ledger/recent-decisions.sh --limit=10

# Search by IA
./scripts/ledger/search.sh --ia=ia-developer --success=true --limit=20

# Search by problem type
./scripts/ledger/search.sh --type=security --period=last-month

# Search by keywords
./scripts/ledger/search.sh --keywords="authentication,oauth" --limit=10

# Full-text search
./scripts/ledger/search.sh --query="microservices architecture"

# Export for analysis
./scripts/ledger/export.sh \
  --format=csv \
  --period=last-quarter \
  --output=decisions-q1-2025.csv

# Analytics
./scripts/ledger/analytics.sh --period=last-month
```

### Automatic ADR Generation

```bash
# Generate ADR from decision
./scripts/ledger/generate-adr.sh --decision-id=DEC-2025-127

# Auto-generate ADRs for significant decisions
./scripts/ledger/auto-generate-adrs.sh \
  --period=last-week \
  --min-significance=high
```

---

## Performance Optimization

### Monitoring Squad Performance

```bash
# Real-time squad dashboard
./scripts/monitoring/squad-dashboard.sh

# Performance metrics
./scripts/monitoring/performance-metrics.sh --period=last-week
```

### Optimization Strategies

```yaml
yamloptimization_strategies:
  
  parallel_execution:
    description: "Run independent tasks simultaneously"
    when_to_use:
      - "Tasks don't depend on each other"
      - "Different IAs available"
      - "Time-critical project"
    
    example: |
      Sequential (slow):
        ia-designer → ia-developer → ia-qa
        Total: 6 hours
      
      Parallel (fast):
        ia-designer (mockups)        ─┐
        ia-arquiteto (API design)     ├─→ ia-developer → ia-qa
        ia-data-architect (DB schema)─┘
        Total: 4 hours
    
    command: |
      ./scripts/orchestrator/parallel-execute.sh \
        --tasks="design_ui,design_api,design_db" \
        --ias="ia-designer,ia-arquiteto,ia-data-architect" \
        --sync-at=ia-developer

  batch_processing:
    description: "Group similar tasks for efficiency"
    when_to_use:
      - "Multiple similar tasks"
      - "Context switching is expensive"
      - "Can wait for batch to complete"
    
    example: |
      Individual (slow):
        Fix bug A → handoff → Fix bug B → handoff → Fix bug C
        Total: 3 hours (1h each + handoff overhead)
      
      Batch (fast):
        Fix bugs A, B, C together → single handoff
        Total: 2 hours
    
    command: |
      ./scripts/orchestrator/batch-execute.sh \
        --ia=ia-developer \
        --tasks="bug-fix-123,bug-fix-124,bug-fix-125" \
        --batch-mode=sequential

  caching_decisions:
    description: "Reuse previous decisions for similar problems"
    when_to_use:
      - "Problem seen before"
      - "Context hasn't changed significantly"
      - "Previous solution was successful"
    
    example: |
      Problem: "Implement pagination for product list"
      Cache hit: Similar problem solved 2 months ago
      Reuse: 90% of previous solution + 10% adaptation
      Time saved: 70%
    
    command: |
      ./scripts/orchestrator/route-problem.sh \
        --query="Implement pagination for orders" \
        --use-cache=true \
        --similarity-threshold=0.85

  preemptive_routing:
    description: "Route problems before they're fully specified"
    when_to_use:
      - "Clear which IA will handle it"
      - "Can start preparatory work"
      - "Reduce overall latency"
    
    example: |
      Traditional:
        Requirements gathered → Analyzed → Routed → IA starts
        Latency: 30 minutes before work begins
      
      Preemptive:
        Initial keywords detected → IA notified → Prepares → Starts immediately
        Latency: 5 minutes
    
    command: |
      ./scripts/orchestrator/preemptive-route.sh \
        --keywords="security,authentication,oauth" \
        --likely-ia=ia-auditor \
        --notify-early=true
```

### Performance Tuning

```bash
# Identify bottlenecks
./scripts/monitoring/identify-bottlenecks.sh

# Optimize specific IA
./scripts/monitoring/optimize-ia.sh --ia=ia-developer

# A/B test routing strategies
./scripts/monitoring/ab-test-routing.sh \
  --variant-a=historical \
  --variant-b=ml-based \
  --sample-size=50 \
  --metric=confidence
```

---

## Troubleshooting

### Common Issues

```yaml
yamlcommon_issues:
  
  low_routing_confidence:
    symptoms:
      - "Confidence scores consistently < 0.70"
      - "Frequent human escalations"
      - "IAs unsure which tasks to take"
    
    causes:
      - "Insufficient training data"
      - "Problem type not in activation matrix"
      - "Ambiguous problem description"
    
    solutions:
      - "Add more examples to Auto-RAG"
      - "Update activation matrix with new patterns"
      - "Clarify problem statement with more context"
      - "Manually route and capture for learning"
    
    commands: |
      ./scripts/troubleshooting/routing-confidence.sh
      ./scripts/learning/add-training-example.sh \
        --problem="Your problem description" \
        --correct-ia=ia-developer \
        --confidence=0.95
      nano .buildtovalue/orchestration/activation-matrix.yaml
  
  handoff_failures:
    symptoms:
      - "Handoffs taking > 15 minutes"
      - "Target IA requests clarification"
      - "Context loss between IAs"
    
    causes:
      - "Incomplete CIIF protocol"
      - "Missing artifacts"
      - "Unclear success criteria"
      - "Ambiguous terminology"
    
    solutions:
      - "Use CIIF template strictly"
      - "Verify all artifacts before handoff"
      - "Define clear acceptance criteria"
      - "Use ubiquitous language from domain model"
    
    commands: |
      ./scripts/orchestrator/validate-handoff.sh \
        --ciif-file=./handoffs/my-handoff.yaml
      ./scripts/troubleshooting/handoff-analysis.sh \
        --period=last-week
      ./scripts/orchestrator/generate-handoff-template.sh \
        --from=ia-arquiteto \
        --to=ia-developer
  
  conflict_escalation:
    symptoms:
      - "Conflicts not resolving at Level 1 or 2"
      - "Same IAs conflicting repeatedly"
      - "Resolution taking > 2 hours"
    
    causes:
      - "Fundamental disagreement in mental models"
      - "Unclear decision rights"
      - "Missing information"
      - "Personal/stylistic preferences"
    
    solutions:
      - "Clarify decision authority matrix"
      - "Reference shared principles (books)"
      - "Gather missing information first"
      - "Focus on outcomes, not approaches"
      - "Use expert arbitration earlier"
    
    commands: |
      ./scripts/troubleshooting/conflict-patterns.sh
      ./scripts/orchestrator/resolve-conflict.sh \
        --conflict-id=CONF-2025-XXX \
        --method=expert_arbitration \
        --arbiter=ia-arquiteto
      ./scripts/orchestrator/update-decision-rights.sh
  
  performance_degradation:
    symptoms:
      - "Decision time increasing"
      - "Success rate declining"
      - "Cost per decision rising"
    
    causes:
      - "Auto-RAG index too large"
      - "IA confidence decreasing"
      - "Complexity of problems increasing"
      - "Resource constraints"
    
    solutions:
      - "Optimize RAG index"
      - "Review and adjust autonomy levels"
      - "Analyze problem complexity trends"
      - "Scale infrastructure"
      - "Provide additional training"
    
    commands: |
      ./scripts/troubleshooting/performance-diagnostic.sh
      ./scripts/learning/optimize-rag-index.sh
      ./scripts/orchestrator/reset-ia.sh --ia=ia-developer
  
  cost_overruns:
    symptoms:
      - "Monthly cost > budget"
      - "Expensive IAs overused"
      - "Redundant operations"
    
    causes:
      - "No cost constraints in routing"
      - "Inefficient decision processes"
      - "Lack of caching"
      - "Over-engineering"
    
    solutions:
      - "Set cost limits in routing"
      - "Enable decision caching"
      - "Use cheaper IAs for simple tasks"
      - "Batch similar operations"
      - "Optimize prompts"
    
    commands: |
      ./scripts/monitoring/cost-analysis.sh --period=last-month
      ./scripts/orchestrator/set-cost-limit.sh \
        --daily=10.00 \
        --per-decision=0.20
      ./scripts/orchestrator/enable-caching.sh \
        --similarity-threshold=0.90
  
  autonomy_issues:
    symptoms:
      - "IA making poor decisions autonomously"
      - "Too many human escalations"
      - "Autonomy level fluctuating"
    
    causes:
      - "Insufficient training"
      - "Domain shift (new problem types)"
      - "Incorrect confidence calibration"
      - "Autonomy level too high/low"
    
    solutions:
      - "Adjust autonomy thresholds"
      - "Provide targeted training"
      - "Recalibrate confidence scoring"
      - "Manual review of recent decisions"
    
    commands: |
      ./scripts/troubleshooting/autonomy-audit.sh --ia=ia-developer
      ./scripts/orchestrator/recalibrate-confidence.sh \
        --ia=ia-developer \
        --based-on=last-50-decisions
      ./scripts/orchestrator/temporary-autonomy.sh \
        --ia=ia-developer \
        --level=2 \
        --duration=7days
```

### Diagnostic Tools

```bash
# Comprehensive health check
./scripts/troubleshooting/health-check.sh

# Deep dive on specific IA
./scripts/troubleshooting/ia-diagnostic.sh --ia=ia-developer

# Trace a specific decision
./scripts/troubleshooting/trace-decision.sh --id=DEC-2025-127

# Network visualization of dependencies
./scripts/troubleshooting/visualize-dependencies.sh

# Debug mode (verbose logging)
./scripts/orchestrator/set-debug-mode.sh --enable
```

---

## Best Practices

1. **Context First:** Always structure handoffs using the CIIF protocol.
2. **Confidence Calibration:** Review routing accuracy weekly and adjust thresholds.
3. **Ethics Integration:** Involve IA-Ethics-Guardian for data, privacy, and automation topics.
4. **Ledger Discipline:** No decision is complete until logged with artifacts and outcomes.
5. **Learning Loop:** Use decision retrospectives to update mental models and activation rules.

---

## Advanced Techniques

- **Preemptive Conflict Mitigation:** Run `detect-conflict.sh` before routing high-stakes decisions to pre-align stakeholders.
- **Autonomy by Domain:** Configure conditional autonomy levels per IA using `conditional-autonomy.sh` for nuanced control.
- **Cross-Squad Syncs:** Use `broadcast.sh` with squad-wide updates to align mental models weekly.
- **Scenario Simulations:** Run `simulate-sprint.sh` with historic backlogs to stress-test routing and handoff configurations.
- **Ethical Sandboxing:** Trigger `run-ethics-review.sh` in dry-run mode to assess new features before production planning.

---

**Document Version:** 7.0.0  
**Last Updated:** 2025-01-20  
**Maintained By:** BuildToValue Squad Team  
© 2025 BuildToValue | Main Documentation | Architecture
