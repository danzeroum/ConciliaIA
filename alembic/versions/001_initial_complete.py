"""Initial complete database schema

Revision ID: 001_initial_complete
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

revision = '001_initial_complete'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ========== TENANTS ==========
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('org_name', sa.String(255), nullable=False),
        sa.Column('cnpj', sa.String(18), unique=True, nullable=False),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('features', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('rate_limit', sa.Integer, nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_tenants_cnpj', 'tenants', ['cnpj'], unique=True)
    op.create_index('idx_tenants_tier', 'tenants', ['tier'])
    op.create_index('idx_tenants_active', 'tenants', ['active'])

    # ========== USERS ==========
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('roles', postgresql.JSONB, nullable=False, server_default=text("'[\"user\"]'::jsonb")),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # ========== SALES ==========
    op.create_table(
        'sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nsu', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default="'BRL'"),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('authorization_code', sa.String(50)),
        sa.Column('installments', sa.Integer, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_sales_tenant_id', 'sales', ['tenant_id'])
    op.create_index('idx_sales_nsu', 'sales', ['nsu'])
    op.create_index('idx_sales_date', 'sales', ['date'])
    op.create_index('idx_sales_tenant_date', 'sales', ['tenant_id', 'date'])

    # ========== ACQUIRER TRANSACTIONS ==========
    op.create_table(
        'acquirer_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('acquirer', sa.String(50), nullable=False),
        sa.Column('nsu', sa.String(50), nullable=False),
        sa.Column('authorization_code', sa.String(50)),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default="'BRL'"),
        sa.Column('transaction_date', sa.DateTime, nullable=False),
        sa.Column('settlement_date', sa.Date),
        sa.Column('transaction_time', sa.String(8)),
        sa.Column('card_brand', sa.String(20)),
        sa.Column('card_number_masked', sa.String(20)),
        sa.Column('product_type', sa.String(50)),
        sa.Column('terminal_id', sa.String(50)),
        sa.Column('gross_amount', sa.Numeric(15, 2)),
        sa.Column('mdr_rate', sa.Numeric(5, 4)),
        sa.Column('mdr_amount', sa.Numeric(15, 2)),
        sa.Column('net_amount', sa.Numeric(15, 2)),
        sa.Column('installments', sa.Integer, server_default='1'),
        sa.Column('installment_number', sa.Integer),
        sa.Column('batch_number', sa.String(50)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('import_source', sa.String(50)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_acquirer_transactions_tenant_id', 'acquirer_transactions', ['tenant_id'])
    op.create_index('idx_acquirer_transactions_acquirer', 'acquirer_transactions', ['acquirer'])
    op.create_index('idx_acquirer_transactions_nsu', 'acquirer_transactions', ['nsu'])
    op.create_index('idx_acquirer_transactions_transaction_date', 'acquirer_transactions', ['transaction_date'])
    op.create_index('idx_acquirer_transactions_settlement_date', 'acquirer_transactions', ['settlement_date'])

    # ========== RECONCILIATION MATCHES ==========
    op.create_table(
        'reconciliation_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('acquirer_transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('match_type', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=False),
        sa.Column('validated', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('validated_by', sa.String(100)),
        sa.Column('validated_at', sa.DateTime),
        sa.Column('matched_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_reconciliation_matches_tenant_id', 'reconciliation_matches', ['tenant_id'])
    op.create_index('idx_reconciliation_matches_sale_id', 'reconciliation_matches', ['sale_id'])
    op.create_index('idx_reconciliation_matches_transaction_id', 'reconciliation_matches', ['transaction_id'])

    # ========== BANK TRANSACTIONS ==========
    op.create_table(
        'bank_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bank_account_id', sa.String(64), nullable=False),
        sa.Column('bank_transaction_id', sa.String(120)),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('memo', sa.Text),
        sa.Column('description_user_friendly', sa.Text),
        sa.Column('payee', sa.String(255)),
        sa.Column('check_number', sa.String(50)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_bank_transactions_tenant_id', 'bank_transactions', ['tenant_id'])
    op.create_index('idx_bank_transactions_bank_account_id', 'bank_transactions', ['bank_account_id'])
    op.create_index('idx_bank_transactions_bank_transaction_id', 'bank_transactions', ['bank_transaction_id'])
    op.create_index('idx_bank_transactions_transaction_date', 'bank_transactions', ['transaction_date'])

    # ========== BANK RECONCILIATIONS ==========
    op.create_table(
        'bank_reconciliations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bank_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bank_transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('acquirer_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('acquirer_transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=False),
        sa.Column('match_type', sa.String(50), nullable=False),
        sa.Column('validated', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('validated_by', sa.String(100)),
        sa.Column('validated_at', sa.DateTime),
        sa.Column('matched_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_bank_reconciliations_tenant_id', 'bank_reconciliations', ['tenant_id'])
    op.create_index('idx_bank_reconciliations_bank_transaction_id', 'bank_reconciliations', ['bank_transaction_id'])
    op.create_index('idx_bank_reconciliations_acquirer_transaction_id', 'bank_reconciliations', ['acquirer_transaction_id'])

    # ========== DIVERGENCES ==========
    op.create_table(
        'divergences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('divergence_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reconciliation_matches.id', ondelete='SET NULL')),
        sa.Column('expected_value', sa.Numeric(15, 2)),
        sa.Column('actual_value', sa.Numeric(15, 2)),
        sa.Column('suggested_action', sa.Text),
        sa.Column('status', sa.String(20), nullable=False, server_default="'open'"),
        sa.Column('detected_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('resolved_at', sa.DateTime),
    )
    op.create_index('idx_divergences_tenant_id', 'divergences', ['tenant_id'])
    op.create_index('idx_divergences_divergence_type', 'divergences', ['divergence_type'])
    op.create_index('idx_divergences_severity', 'divergences', ['severity'])
    op.create_index('idx_divergences_status', 'divergences', ['status'])

    # ========== SETTLEMENTS ==========
    op.create_table(
        'settlements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('acquirer_transactions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expected_date', sa.Date, nullable=False),
        sa.Column('actual_date', sa.Date),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default="'pending'"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_settlements_tenant_id', 'settlements', ['tenant_id'])
    op.create_index('idx_settlements_expected_date', 'settlements', ['expected_date'])
    op.create_index('idx_settlements_status', 'settlements', ['status'])

    # ========== IMPORT SCHEDULES ==========
    op.create_table(
        'import_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('acquirer', sa.String(50), nullable=False),
        sa.Column('schedule_type', sa.String(20), nullable=False),
        sa.Column('time_of_day', sa.String(5), nullable=False),
        sa.Column('days_to_import', sa.Integer, nullable=False, server_default='1'),
        sa.Column('credentials_encrypted', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('last_run', sa.DateTime),
        sa.Column('last_status', sa.String(20)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=text('now()')),
    )
    op.create_index('idx_import_schedules_tenant_id', 'import_schedules', ['tenant_id'])

    # ========== NOTIFICATIONS ==========
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default="'info'"),
        sa.Column('action_url', sa.String(500)),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('read_at', sa.DateTime),
    )
    op.create_index('idx_notifications_tenant_id', 'notifications', ['tenant_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])

    # ========== ALERT HISTORY ==========
    op.create_table(
        'alert_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_id', sa.String(50), nullable=False),
        sa.Column('triggered_at', sa.DateTime, nullable=False, server_default=text('now()')),
        sa.Column('alert_data', postgresql.JSONB),
    )
    op.create_index('idx_alert_history_tenant_id', 'alert_history', ['tenant_id'])
    op.create_index('idx_alert_history_rule_id', 'alert_history', ['rule_id'])


def downgrade():
    op.drop_table('alert_history')
    op.drop_table('notifications')
    op.drop_table('import_schedules')
    op.drop_table('settlements')
    op.drop_table('divergences')
    op.drop_table('bank_reconciliations')
    op.drop_table('bank_transactions')
    op.drop_table('reconciliation_matches')
    op.drop_table('acquirer_transactions')
    op.drop_table('sales')
    op.drop_table('users')
    op.drop_table('tenants')
