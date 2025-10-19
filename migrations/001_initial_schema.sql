-- Initial schema for ConciliaAI multi-tenant reconciliation platform.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('alpha', 'beta', 'growth', 'scale', 'enterprise')),
    active BOOLEAN DEFAULT TRUE,
    features JSONB DEFAULT '[]'::jsonb,
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tenants_active ON tenants(active);
CREATE INDEX idx_tenants_tier ON tenants(tier);

CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nsu VARCHAR(50) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    date DATE NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    authorization_code VARCHAR(50),
    installments INTEGER DEFAULT 1 CHECK (installments BETWEEN 1 AND 12),
    matched BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_tenant_nsu UNIQUE (tenant_id, nsu)
);

CREATE INDEX idx_sales_tenant_unmatched ON sales(tenant_id, matched, date) WHERE matched = FALSE;
CREATE INDEX idx_sales_nsu_trgm ON sales USING GIN (nsu gin_trgm_ops);
CREATE INDEX idx_sales_date ON sales(date DESC);

CREATE TABLE acquirer_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    acquirer VARCHAR(50) NOT NULL CHECK (acquirer IN ('cielo', 'rede', 'stone', 'mercadopago')),
    nsu VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    settlement_date DATE NOT NULL,
    gross_amount NUMERIC(15, 2) NOT NULL,
    mdr_fee NUMERIC(15, 2) NOT NULL,
    net_amount NUMERIC(15, 2) NOT NULL,
    installments INTEGER DEFAULT 1,
    installment_number INTEGER,
    matched BOOLEAN DEFAULT FALSE,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_tenant_acquirer_nsu UNIQUE (tenant_id, acquirer, nsu)
);

CREATE INDEX idx_transactions_tenant_unmatched ON acquirer_transactions(tenant_id, matched, transaction_date)
    WHERE matched = FALSE;
CREATE INDEX idx_transactions_nsu_trgm ON acquirer_transactions USING GIN (nsu gin_trgm_ops);
CREATE INDEX idx_transactions_settlement ON acquirer_transactions(tenant_id, settlement_date);

CREATE TABLE reconciliation_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES acquirer_transactions(id) ON DELETE CASCADE,
    match_type VARCHAR(20) NOT NULL CHECK (match_type IN ('exact', 'fuzzy_amount', 'fuzzy_date', 'installment', 'ml_predicted')),
    confidence NUMERIC(3, 2) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    matched_at TIMESTAMP DEFAULT NOW(),
    reviewed_by VARCHAR(255),
    approved BOOLEAN DEFAULT FALSE,
    notes TEXT,
    CONSTRAINT unique_sale_match UNIQUE (sale_id)
);

CREATE INDEX idx_matches_tenant ON reconciliation_matches(tenant_id, matched_at DESC);
CREATE INDEX idx_matches_confidence ON reconciliation_matches(confidence) WHERE approved = FALSE;

CREATE TABLE divergences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    sale_id UUID REFERENCES sales(id),
    transaction_id UUID REFERENCES acquirer_transactions(id),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    amount_at_risk NUMERIC(15, 2) NOT NULL,
    variance_percent NUMERIC(5, 2),
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution TEXT,
    notified BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

CREATE INDEX idx_divergences_tenant_open ON divergences(tenant_id, resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX idx_divergences_severity ON divergences(severity, detected_at DESC);
CREATE INDEX idx_divergences_type ON divergences(type);

CREATE TABLE acquirer_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    acquirer VARCHAR(50) NOT NULL,
    credentials_encrypted BYTEA NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_tenant_acquirer UNIQUE (tenant_id, acquirer)
);

CREATE INDEX idx_credentials_tenant_active ON acquirer_credentials(tenant_id, active);

CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_created ON audit_trail(tenant_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_trail(action, created_at DESC);

CREATE TABLE reconciliation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    matched_count INTEGER DEFAULT 0,
    divergence_count INTEGER DEFAULT 0,
    accuracy NUMERIC(5, 2),
    processing_time_ms INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_tenant_status ON reconciliation_jobs(tenant_id, status, created_at DESC);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_updated_at
    BEFORE UPDATE ON sales
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON acquirer_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE acquirer_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE divergences ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_sales ON sales
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE POLICY tenant_isolation_transactions ON acquirer_transactions
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE OR REPLACE FUNCTION get_reconciliation_stats(
    p_tenant_id UUID,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    total_sales BIGINT,
    total_transactions BIGINT,
    matched BIGINT,
    divergences BIGINT,
    accuracy NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM sales WHERE tenant_id = p_tenant_id AND date BETWEEN p_start_date AND p_end_date) AS total_sales,
        (SELECT COUNT(*) FROM acquirer_transactions WHERE tenant_id = p_tenant_id AND transaction_date BETWEEN p_start_date AND p_end_date) AS total_transactions,
        (SELECT COUNT(*) FROM reconciliation_matches WHERE tenant_id = p_tenant_id AND matched_at::date BETWEEN p_start_date AND p_end_date) AS matched,
        (SELECT COUNT(*) FROM divergences WHERE tenant_id = p_tenant_id AND detected_at::date BETWEEN p_start_date AND p_end_date AND resolved_at IS NULL) AS divergences,
        CASE
            WHEN (SELECT COUNT(*) FROM sales WHERE tenant_id = p_tenant_id AND date BETWEEN p_start_date AND p_end_date) > 0 THEN
                (SELECT COUNT(*) FROM reconciliation_matches WHERE tenant_id = p_tenant_id AND matched_at::date BETWEEN p_start_date AND p_end_date)::NUMERIC /
                (SELECT COUNT(*) FROM sales WHERE tenant_id = p_tenant_id AND date BETWEEN p_start_date AND p_end_date)::NUMERIC * 100
            ELSE 0
        END AS accuracy;
END;
$$ LANGUAGE plpgsql;
