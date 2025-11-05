-- ============================================
-- ConciliaAI - Complete Database Schema
-- ============================================

-- Tenants (com TODAS as colunas que o app espera)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    tier VARCHAR(50) NOT NULL DEFAULT 'alpha',
    active BOOLEAN NOT NULL DEFAULT true,
    features JSONB DEFAULT '[]'::jsonb,
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tenants_active_tier ON tenants(active, tier);
CREATE INDEX IF NOT EXISTS ix_tenants_active ON tenants(active);
CREATE INDEX IF NOT EXISTS ix_tenants_cnpj ON tenants(cnpj);
CREATE INDEX IF NOT EXISTS ix_tenants_tier ON tenants(tier);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS ix_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- Acquirer Transactions
-- Acquirer Transactions (VERSÃO COMPLETA COM TODAS AS COLUNAS)
CREATE TABLE IF NOT EXISTS acquirer_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    acquirer VARCHAR(100) NOT NULL,
    nsu VARCHAR(50) NOT NULL,
    authorization_code VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    transaction_time TIME,
    card_brand VARCHAR(50),
    card_last_4 VARCHAR(4),
    mdr_rate DECIMAL(5,4),
    mdr_amount DECIMAL(15,2),
    net_amount DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'pending',
    installment_current INTEGER DEFAULT 1,
    installment_total INTEGER DEFAULT 1,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_nsu_trgm ON acquirer_transactions USING gin(nsu gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant_acquirer ON acquirer_transactions(tenant_id, acquirer);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant_date ON acquirer_transactions(tenant_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant_settlement ON acquirer_transactions(tenant_id, settlement_date);
CREATE INDEX IF NOT EXISTS ix_acquirer_transactions_tenant_id ON acquirer_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS ix_acquirer_transactions_nsu ON acquirer_transactions(nsu);
CREATE INDEX IF NOT EXISTS ix_acquirer_transactions_acquirer ON acquirer_transactions(acquirer);
CREATE INDEX IF NOT EXISTS ix_acquirer_transactions_transaction_date ON acquirer_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS ix_acquirer_transactions_settlement_date ON acquirer_transactions(settlement_date);
-- Sales
-- Sales (VERSÃO COMPLETA)
CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nsu VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    payment_method VARCHAR(50),
    authorization_code VARCHAR(100),
    installments INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_nsu_trgm ON sales USING gin(nsu gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sales_tenant_date ON sales(tenant_id, date);
CREATE INDEX IF NOT EXISTS idx_sales_tenant_nsu ON sales(tenant_id, nsu);
CREATE INDEX IF NOT EXISTS ix_sales_tenant_id ON sales(tenant_id);
CREATE INDEX IF NOT EXISTS ix_sales_nsu ON sales(nsu);
CREATE INDEX IF NOT EXISTS ix_sales_date ON sales(date);

-- Bank Transactions
CREATE TABLE IF NOT EXISTS bank_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    bank_account_id UUID NOT NULL,
    bank_transaction_id VARCHAR(255) NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    is_reconciled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bank_transactions_fitid ON bank_transactions(tenant_id, bank_account_id, bank_transaction_id);
CREATE INDEX IF NOT EXISTS ix_bank_transactions_tenant_id ON bank_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS ix_bank_transactions_bank_account_id ON bank_transactions(bank_account_id);
CREATE INDEX IF NOT EXISTS ix_bank_transactions_bank_transaction_id ON bank_transactions(bank_transaction_id);
CREATE INDEX IF NOT EXISTS ix_bank_transactions_is_reconciled ON bank_transactions(is_reconciled);
CREATE INDEX IF NOT EXISTS ix_bank_transactions_transaction_date ON bank_transactions(transaction_date);

-- Import Schedules (FALTAVA!)
CREATE TABLE IF NOT EXISTS import_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    acquirer VARCHAR(100) NOT NULL,
    schedule_type VARCHAR(50) NOT NULL,
    time_of_day TIME,
    days_to_import INTEGER DEFAULT 7,
    credential_hint VARCHAR(255),
    webhook_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_import_schedules_active ON import_schedules(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_import_schedules_tenant ON import_schedules(tenant_id);
CREATE INDEX IF NOT EXISTS ix_import_schedules_tenant_id ON import_schedules(tenant_id);
CREATE INDEX IF NOT EXISTS ix_import_schedules_is_active ON import_schedules(is_active);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_tenant_created ON notifications(tenant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(tenant_id, is_read);
CREATE INDEX IF NOT EXISTS ix_notifications_tenant_id ON notifications(tenant_id);
CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications(is_read);

-- Alert History
CREATE TABLE IF NOT EXISTS alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    rule_id UUID NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alert_history_rule ON alert_history(rule_id, triggered_at);
CREATE INDEX IF NOT EXISTS idx_alert_history_tenant ON alert_history(tenant_id, triggered_at);
CREATE INDEX IF NOT EXISTS ix_alert_history_tenant_id ON alert_history(tenant_id);
CREATE INDEX IF NOT EXISTS ix_alert_history_rule_id ON alert_history(rule_id);

-- Bank Reconciliations
CREATE TABLE IF NOT EXISTS bank_reconciliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    bank_transaction_id UUID NOT NULL REFERENCES bank_transactions(id) ON DELETE CASCADE,
    acquirer_transaction_id UUID NOT NULL REFERENCES acquirer_transactions(id) ON DELETE CASCADE,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bank_reconciliations_tenant ON bank_reconciliations(tenant_id, matched_at);
CREATE INDEX IF NOT EXISTS ix_bank_reconciliations_tenant_id ON bank_reconciliations(tenant_id);
CREATE INDEX IF NOT EXISTS ix_bank_reconciliations_bank_transaction_id ON bank_reconciliations(bank_transaction_id);
CREATE INDEX IF NOT EXISTS ix_bank_reconciliations_acquirer_transaction_id ON bank_reconciliations(acquirer_transaction_id);

-- Reconciliation Matches
CREATE TABLE IF NOT EXISTS reconciliation_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES acquirer_transactions(id) ON DELETE CASCADE,
    confidence DECIMAL(5,4) NOT NULL,
    validated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_matches_confidence ON reconciliation_matches(confidence);
CREATE INDEX IF NOT EXISTS idx_matches_tenant_validated ON reconciliation_matches(tenant_id, validated);
CREATE INDEX IF NOT EXISTS ix_reconciliation_matches_tenant_id ON reconciliation_matches(tenant_id);
CREATE INDEX IF NOT EXISTS ix_reconciliation_matches_sale_id ON reconciliation_matches(sale_id);
CREATE INDEX IF NOT EXISTS ix_reconciliation_matches_transaction_id ON reconciliation_matches(transaction_id);

-- Settlements
CREATE TABLE IF NOT EXISTS settlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    expected_date DATE NOT NULL,
    expected_amount DECIMAL(15,2) NOT NULL,
    actual_amount DECIMAL(15,2),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_settlements_expected_date ON settlements(expected_date);
CREATE INDEX IF NOT EXISTS idx_settlements_tenant_status ON settlements(tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_settlements_tenant_id ON settlements(tenant_id);
CREATE INDEX IF NOT EXISTS ix_settlements_expected_date ON settlements(expected_date);
CREATE INDEX IF NOT EXISTS ix_settlements_status ON settlements(status);

-- Divergences
CREATE TABLE IF NOT EXISTS divergences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    divergence_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_divergences_detected_at ON divergences(detected_at);
CREATE INDEX IF NOT EXISTS idx_divergences_tenant_severity ON divergences(tenant_id, severity);
CREATE INDEX IF NOT EXISTS idx_divergences_tenant_status ON divergences(tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_divergences_tenant_id ON divergences(tenant_id);
CREATE INDEX IF NOT EXISTS ix_divergences_divergence_type ON divergences(divergence_type);
CREATE INDEX IF NOT EXISTS ix_divergences_severity ON divergences(severity);
CREATE INDEX IF NOT EXISTS ix_divergences_status ON divergences(status);

-- Alembic version table
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
