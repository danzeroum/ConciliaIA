-- BuildToValue v7.0 - Database Schema
-- PostgreSQL 13+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DECISIONS TABLE
-- Stores all routing and execution decisions
-- ============================================================================

CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Problem details
    problem TEXT NOT NULL,
    problem_type VARCHAR(100),
    complexity VARCHAR(50),
    context JSONB,
    
    -- Routing information
    routing JSONB NOT NULL,
    -- Structure: {
    --   "primary_ia": "ia-developer",
    --   "support_ias": ["ia-qa"],
    --   "confidence": 0.87,
    --   "method": "ml",
    --   "routing_time_ms": 450
    -- }
    
    -- Decision details
    decision JSONB,
    -- Structure: {
    --   "chosen_ia": "ia-developer",
    --   "rationale": "...",
    --   "sequence": [...],
    --   "estimates": {...}
    -- }
    
    -- Execution details
    execution JSONB,
    -- Structure: {
    --   "execution_id": "EXEC-...",
    --   "started_at": "...",
    --   "completed_at": "...",
    --   "success": true,
    --   "artifacts": [...],
    --   "handoffs": [...]
    -- }
    
    -- Outcome and learning
    outcome JSONB,
    -- Structure: {
    --   "success": true,
    --   "actual_cost": 0.15,
    --   "actual_duration": 1.2,
    --   "quality_score": 0.92,
    --   "lessons_learned": "...",
    --   "feedback": {...}
    -- }
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Indexes for decisions
CREATE INDEX idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX idx_decisions_problem_type ON decisions(problem_type);
CREATE INDEX idx_decisions_routing_ia ON decisions((routing->>'primary_ia'));
CREATE INDEX idx_decisions_success ON decisions((execution->>'success'));
CREATE INDEX idx_decisions_created_at ON decisions(created_at DESC);
CREATE INDEX idx_decisions_context ON decisions USING GIN(context);

-- ============================================================================
-- PERSONAS TABLE
-- Stores IA persona configurations
-- ============================================================================

CREATE TABLE IF NOT EXISTS personas (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    version VARCHAR(20) DEFAULT '7.0',
    
    -- Persona configuration
    config JSONB NOT NULL,
    -- Structure: {
    --   "identity": {...},
    --   "mental_models": {...},
    --   "activation_triggers": {...},
    --   "capabilities": {...}
    -- }
    
    -- Autonomy
    autonomy_level INTEGER DEFAULT 3 CHECK (autonomy_level BETWEEN 1 AND 5),
    autonomy_history JSONB,
    
    -- Performance metrics
    metrics JSONB,
    -- Structure: {
    --   "total_activations": 123,
    --   "success_rate": 0.94,
    --   "avg_confidence": 0.87,
    --   "avg_execution_time": 540
    -- }
    
    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for personas
CREATE INDEX idx_personas_active ON personas(active);
CREATE INDEX idx_personas_autonomy ON personas(autonomy_level);

-- ============================================================================
-- HANDOFFS TABLE
-- Stores inter-IA handoffs (CIIF protocol)
-- ============================================================================

CREATE TABLE IF NOT EXISTS handoffs (
    id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) REFERENCES decisions(id),
    
    -- Handoff parties
    from_ia VARCHAR(100) NOT NULL,
    to_ia VARCHAR(100) NOT NULL,
    
    -- CIIF protocol data
    context JSONB NOT NULL,
    information JSONB NOT NULL,
    intention JSONB NOT NULL,
    format JSONB NOT NULL,
    
    -- Artifacts
    artifacts JSONB,
    -- Structure: [
    --   {"type": "code", "path": "...", "description": "..."},
    --   {"type": "document", "path": "...", "description": "..."}
    -- ]
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending',
    -- Values: pending, in_progress, completed, failed, rejected
    
    validation JSONB,
    -- Structure: {
    --   "validated_by": "ia-qa",
    --   "validated_at": "...",
    --   "validation_result": {...}
    -- }
    
    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER
);

-- Indexes for handoffs
CREATE INDEX idx_handoffs_decision ON handoffs(decision_id);
CREATE INDEX idx_handoffs_from_ia ON handoffs(from_ia);
CREATE INDEX idx_handoffs_to_ia ON handoffs(to_ia);
CREATE INDEX idx_handoffs_status ON handoffs(status);
CREATE INDEX idx_handoffs_created_at ON handoffs(created_at DESC);

-- ============================================================================
-- CONFLICTS TABLE
-- Stores inter-IA conflicts and resolutions
-- ============================================================================

CREATE TABLE IF NOT EXISTS conflicts (
    id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) REFERENCES decisions(id),
    
    -- Conflict parties
    ias_involved JSONB NOT NULL,
    -- Structure: ["ia-developer", "ia-arquiteto"]
    
    -- Conflict details
    conflict_type VARCHAR(100) NOT NULL,
    -- Values: technical, business, security, ethical, priority
    
    description TEXT NOT NULL,
    positions JSONB NOT NULL,
    -- Structure: {
    --   "ia-developer": {"position": "...", "rationale": "..."},
    --   "ia-arquiteto": {"position": "...", "rationale": "..."}
    -- }
    
    -- Resolution
    resolution_level INTEGER,
    -- Values: 1 (negotiation), 2 (voting), 3 (arbitration), 4 (human)
    
    resolution JSONB,
    -- Structure: {
    --   "method": "expert_arbitration",
    --   "arbiter": "ia-arquiteto",
    --   "decision": "...",
    --   "rationale": "..."
    -- }
    
    -- Status
    status VARCHAR(50) DEFAULT 'open',
    -- Values: open, in_resolution, resolved, escalated
    
    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution_time_seconds INTEGER
);

-- Indexes for conflicts
CREATE INDEX idx_conflicts_decision ON conflicts(decision_id);
CREATE INDEX idx_conflicts_type ON conflicts(conflict_type);
CREATE INDEX idx_conflicts_status ON conflicts(status);
CREATE INDEX idx_conflicts_created_at ON conflicts(created_at DESC);

-- ============================================================================
-- METRICS TABLE
-- Stores time-series metrics for monitoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Metric identification
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    -- Values: counter, gauge, histogram, summary
    
    -- Metric value
    metric_value NUMERIC NOT NULL,
    
    -- Labels
    labels JSONB,
    -- Structure: {"ia": "ia-developer", "operation": "route"}
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for metrics
CREATE INDEX idx_metrics_name_timestamp ON metrics(metric_name, timestamp DESC);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_labels ON metrics USING GIN(labels);

-- Partition metrics by month (optional, for large datasets)
-- CREATE TABLE metrics_YYYYMM PARTITION OF metrics
--   FOR VALUES FROM ('YYYY-MM-01') TO ('YYYY-MM-01');

-- ============================================================================
-- LESSONS_LEARNED TABLE
-- Stores captured lessons from decisions
-- ============================================================================

CREATE TABLE IF NOT EXISTS lessons_learned (
    id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) REFERENCES decisions(id),
    
    -- Lesson details
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    -- Values: architecture, implementation, testing, deployment, 
    --         performance, security, usability, process, communication
    
    significance VARCHAR(50) DEFAULT 'medium',
    -- Values: low, medium, high
    
    -- Content
    situation TEXT,
    action TEXT,
    result TEXT,
    recommendations TEXT NOT NULL,
    
    -- Tags for searching
    tags TEXT[],
    
    -- Related IAs
    ias_involved TEXT[],
    
    -- Metadata
    captured_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    archived BOOLEAN DEFAULT FALSE
);

-- Indexes for lessons_learned
CREATE INDEX idx_lessons_decision ON lessons_learned(decision_id);
CREATE INDEX idx_lessons_category ON lessons_learned(category);
CREATE INDEX idx_lessons_significance ON lessons_learned(significance);
CREATE INDEX idx_lessons_tags ON lessons_learned USING GIN(tags);
CREATE INDEX idx_lessons_created_at ON lessons_learned(created_at DESC);
CREATE INDEX idx_lessons_archived ON lessons_learned(archived);

-- ============================================================================
-- AUTONOMY_HISTORY TABLE
-- Tracks autonomy level changes for personas
-- ============================================================================

CREATE TABLE IF NOT EXISTS autonomy_history (
    id BIGSERIAL PRIMARY KEY,
    persona_id VARCHAR(100) REFERENCES personas(id),
    
    -- Change details
    old_level INTEGER NOT NULL,
    new_level INTEGER NOT NULL,
    reason TEXT NOT NULL,
    
    -- Context
    trigger_event VARCHAR(200),
    decision_id VARCHAR(50),
    
    -- Who made the change
    changed_by VARCHAR(200),
    -- Values: "system", "human:john@company.com", "ia-product-manager"
    
    -- Timestamp
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for autonomy_history
CREATE INDEX idx_autonomy_persona ON autonomy_history(persona_id);
CREATE INDEX idx_autonomy_changed_at ON autonomy_history(changed_at DESC);

-- ============================================================================
-- COST_TRACKING TABLE
-- Tracks LLM API costs per decision
-- ============================================================================

CREATE TABLE IF NOT EXISTS cost_tracking (
    id BIGSERIAL PRIMARY KEY,
    decision_id VARCHAR(50) REFERENCES decisions(id),
    
    -- Cost details
    provider VARCHAR(50) NOT NULL,
    -- Values: openai, anthropic, google
    
    model VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    -- Values: routing, execution, validation, learning
    
    -- Token usage
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    
    -- Cost
    cost_usd NUMERIC(10, 6) NOT NULL,
    
    -- Metadata
    ia VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for cost_tracking
CREATE INDEX idx_cost_decision ON cost_tracking(decision_id);
CREATE INDEX idx_cost_provider ON cost_tracking(provider);
CREATE INDEX idx_cost_ia ON cost_tracking(ia);
CREATE INDEX idx_cost_timestamp ON cost_tracking(timestamp DESC);

-- ============================================================================
-- AUDIT_LOG TABLE
-- Stores audit trail for compliance (enterprise only)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    -- Values: user_login, permission_change, config_change, 
    --         data_export, deletion, etc.
    
    event_description TEXT NOT NULL,
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL,
    -- Values: user, ia, system
    
    actor_id VARCHAR(200) NOT NULL,
    
    -- Target
    target_type VARCHAR(100),
    target_id VARCHAR(200),
    
    -- Details
    details JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for audit_log
CREATE INDEX idx_audit_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_actor ON audit_log(actor_type, actor_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_target ON audit_log(target_type, target_id);

-- ============================================================================
-- VIEWS
-- Convenient views for common queries
-- ============================================================================

-- Recent successful decisions
CREATE OR REPLACE VIEW recent_successful_decisions AS
SELECT 
    d.id,
    d.timestamp,
    d.problem,
    d.problem_type,
    d.routing->>'primary_ia' as primary_ia,
    d.execution->>'success' as success,
    d.outcome->>'quality_score' as quality_score
FROM decisions d
WHERE d.execution->>'success' = 'true'
ORDER BY d.timestamp DESC
LIMIT 100;

-- Persona performance summary
CREATE OR REPLACE VIEW persona_performance AS
SELECT 
    p.id,
    p.name,
    p.autonomy_level,
    p.metrics->>'total_activations' as total_activations,
    p.metrics->>'success_rate' as success_rate,
    p.metrics->>'avg_confidence' as avg_confidence,
    p.active
FROM personas p
WHERE p.active = true
ORDER BY p.name;

-- Daily cost summary
CREATE OR REPLACE VIEW daily_costs AS
SELECT 
    DATE(timestamp) as date,
    provider,
    SUM(cost_usd) as total_cost,
    SUM(total_tokens) as total_tokens,
    COUNT(*) as operations
FROM cost_tracking
GROUP BY DATE(timestamp), provider
ORDER BY date DESC;

-- Conflict resolution effectiveness
CREATE OR REPLACE VIEW conflict_stats AS
SELECT 
    conflict_type,
    COUNT(*) as total_conflicts,
    AVG(resolution_time_seconds) as avg_resolution_time,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated
FROM conflicts
GROUP BY conflict_type;

-- ============================================================================
-- FUNCTIONS
-- Utility functions
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_decisions_updated_at 
    BEFORE UPDATE ON decisions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personas_updated_at 
    BEFORE UPDATE ON personas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lessons_updated_at 
    BEFORE UPDATE ON lessons_learned 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate handoff duration
CREATE OR REPLACE FUNCTION calculate_handoff_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND NEW.completed_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.created_at));
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_handoff_duration 
    BEFORE UPDATE ON handoffs 
    FOR EACH ROW EXECUTE FUNCTION calculate_handoff_duration();

-- Function to calculate conflict resolution time
CREATE OR REPLACE FUNCTION calculate_conflict_resolution_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'resolved' AND NEW.resolved_at IS NOT NULL THEN
        NEW.resolution_time_seconds = EXTRACT(EPOCH FROM (NEW.resolved_at - NEW.created_at));
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conflict_resolution_time 
    BEFORE UPDATE ON conflicts 
    FOR EACH ROW EXECUTE FUNCTION calculate_conflict_resolution_time();

-- ============================================================================
-- INITIAL DATA
-- Insert default personas
-- ============================================================================

INSERT INTO personas (id, name, autonomy_level, config, metrics) VALUES
    ('ia-product-manager', 'IA Product Manager', 3, 
     '{"identity": {"role": "Product Manager"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-business-analyst', 'IA Business Analyst', 3, 
     '{"identity": {"role": "Business Analyst"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-arquiteto', 'IA Arquiteto', 3, 
     '{"identity": {"role": "Software Architect"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-developer', 'IA Developer', 3, 
     '{"identity": {"role": "Software Developer"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-qa', 'IA QA', 3, 
     '{"identity": {"role": "Quality Assurance"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-auditor', 'IA Auditor', 4, 
     '{"identity": {"role": "Security Auditor"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-designer', 'IA Designer', 3, 
     '{"identity": {"role": "UX/UI Designer"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-ops', 'IA Ops', 3, 
     '{"identity": {"role": "DevOps Engineer"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-data-architect', 'IA Data Architect', 3, 
     '{"identity": {"role": "Data Architect"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-integration-specialist', 'IA Integration Specialist', 3, 
     '{"identity": {"role": "Integration Specialist"}}', 
     '{"total_activations": 0, "success_rate": 0}'),
    
    ('ia-ethics-guardian', 'IA Ethics Guardian', 4, 
     '{"identity": {"role": "Ethics Guardian"}}', 
     '{"total_activations": 0, "success_rate": 0}')
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- GRANTS
-- Set up permissions
-- ============================================================================

-- Grant permissions to btv_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO btv_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO btv_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO btv_user;

-- ============================================================================
-- MAINTENANCE
-- Recommended maintenance tasks
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE decisions;
ANALYZE personas;
ANALYZE handoffs;
ANALYZE conflicts;
ANALYZE metrics;
ANALYZE lessons_learned;

-- Vacuum to reclaim storage
-- Run periodically: VACUUM ANALYZE;

-- ============================================================================
-- NOTES
-- Schema version: 7.0
-- Last updated: 2025-01-20
-- Compatible with: PostgreSQL 13+
-- ============================================================================

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE '✓ BuildToValue v7.0 schema initialized successfully';
    RAISE NOTICE '  - 11 tables created';
    RAISE NOTICE '  - 11 personas inserted';
    RAISE NOTICE '  - Views and functions configured';
    RAISE NOTICE '  - Ready to use!';
END $$;
