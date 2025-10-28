"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_name', sa.String(255), nullable=False),
        sa.Column('cnpj', sa.String(18), unique=True, nullable=False),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('features', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('rate_limit', sa.Integer, nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_tenants_cnpj', 'tenants', ['cnpj'], unique=True)
    op.create_index('idx_tenants_tier', 'tenants', ['tier'])
    op.create_index('idx_tenants_active', 'tenants', ['active'])
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    
    # Sales table
    op.create_table(
        'sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nsu', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('sale_date', sa.Date, nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('installments', sa.Integer, default=1),
        sa.Column('authorization_code', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_sales_tenant_nsu', 'sales', ['tenant_id', 'nsu'])
    op.create_index('idx_sales_sale_date', 'sales', ['sale_date'])
    
    # Transactions table (acquirer transactions)
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nsu', sa.String(50), nullable=False),
        sa.Column('acquirer', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('card_brand', sa.String(50)),
        sa.Column('authorization_code', sa.String(50)),
        sa.Column('mdr_rate', sa.Numeric(5, 2)),
        sa.Column('mdr_amount', sa.Numeric(15, 2)),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_transactions_tenant_nsu', 'transactions', ['tenant_id', 'nsu'])
    op.create_index('idx_transactions_date', 'transactions', ['transaction_date'])
    
    # Matches table
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id'), nullable=False),
        sa.Column('confidence_score', sa.Numeric(5, 4), nullable=False),
        sa.Column('match_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_matches_sale_id', 'matches', ['sale_id'])
    op.create_index('idx_matches_transaction_id', 'matches', ['transaction_id'])
    
    # Divergences table
    op.create_table(
        'divergences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('divergence_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('severity', sa.String(20), default='medium'),
        sa.Column('status', sa.String(50), default='open'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_divergences_tenant_status', 'divergences', ['tenant_id', 'status'])
    
    # Settlements table
    op.create_table(
        'settlements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('acquirer', sa.String(50), nullable=False),
        sa.Column('settlement_date', sa.Date, nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_settlements_tenant_date', 'settlements', ['tenant_id', 'settlement_date'])


def downgrade():
    op.drop_index('idx_tenants_active', 'tenants')
    op.drop_index('idx_tenants_tier', 'tenants')
    op.drop_index('idx_tenants_cnpj', 'tenants')
    op.drop_table('settlements')
    op.drop_table('divergences')
    op.drop_table('matches')
    op.drop_table('transactions')
    op.drop_table('sales')
    op.drop_table('users')
    op.drop_table('tenants')
