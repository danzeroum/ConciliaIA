"""SQLAlchemy models for PostgreSQL."""

from __future__ import annotations
from sqlalchemy import Time
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TenantModel(Base):
    """Tenant table model."""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_name = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    tier = Column(String(20), nullable=False, index=True)
    active = Column(Boolean, default=True, index=True)
    features = Column(JSONB, default=list)
    rate_limit = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales = relationship("SaleModel", back_populates="tenant", cascade="all, delete-orphan")
    transactions = relationship("TransactionModel", back_populates="tenant", cascade="all, delete-orphan")
    bank_transactions = relationship(
        "BankTransactionModel", back_populates="tenant", cascade="all, delete-orphan"
    )
    bank_reconciliations = relationship(
        "BankReconciliationModel", back_populates="tenant", cascade="all, delete-orphan"
    )
    matches = relationship("MatchModel", back_populates="tenant", cascade="all, delete-orphan")
    divergences = relationship("DivergenceModel", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("UserModel", back_populates="tenant", cascade="all, delete-orphan")
    notifications = relationship(
        "NotificationModel", back_populates="tenant", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_tenants_active_tier", "active", "tier"),)


class SaleModel(Base):
    """Sale table model."""

    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    nsu = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="BRL")
    date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(20), nullable=False)
    authorization_code = Column(String(50))
    installments = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="sales")
    matches = relationship("MatchModel", back_populates="sale")

    __table_args__ = (
        Index("idx_sales_tenant_date", "tenant_id", "date"),
        Index("idx_sales_tenant_nsu", "tenant_id", "nsu"),
        Index("idx_sales_nsu_trgm", "nsu", postgresql_using="gin", postgresql_ops={"nsu": "gin_trgm_ops"}),
    )


class TransactionModel(Base):
    """Acquirer transaction table model."""

    __tablename__ = "acquirer_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    acquirer = Column(String(50), nullable=False, index=True)
    nsu = Column(String(50), nullable=False, index=True)
    authorization_code = Column(String(50))
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="BRL")
    transaction_date = Column(DateTime, nullable=False, index=True)
    settlement_date = Column(Date, index=True)
    transaction_time = Column(Time)
    card_brand = Column(String(20))
    card_last_4 = Column(String(4))
    mdr_rate = Column(Numeric(5, 4))
    mdr_amount = Column(Numeric(15, 2))
    net_amount = Column(Numeric(15, 2))
    status = Column(String(20), default="approved")
    installment_current = Column(Integer)
    installment_total = Column(Integer)
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="transactions")
    matches = relationship("MatchModel", back_populates="transaction")
    bank_reconciliations = relationship(
        "BankReconciliationModel", back_populates="acquirer_transaction"
    )
    settlement = relationship("SettlementModel", back_populates="transaction", uselist=False)

    __table_args__ = (
        Index("idx_transactions_tenant_date", "tenant_id", "transaction_date"),
        Index("idx_transactions_tenant_acquirer", "tenant_id", "acquirer"),
        Index("idx_transactions_tenant_settlement", "tenant_id", "settlement_date"),
        Index(
            "idx_transactions_nsu_trgm",
            "nsu",
            postgresql_using="gin",
            postgresql_ops={"nsu": "gin_trgm_ops"},
        ),
    )


class MatchModel(Base):
    """Reconciliation match table model."""

    __tablename__ = "reconciliation_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("acquirer_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    match_type = Column(String(20), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    validated = Column(Boolean, default=False)
    validated_by = Column(String(100))
    validated_at = Column(DateTime)
    matched_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="matches")
    sale = relationship("SaleModel", back_populates="matches")
    transaction = relationship("TransactionModel", back_populates="matches")
    divergences = relationship("DivergenceModel", back_populates="match")

    __table_args__ = (
        Index("idx_matches_tenant_validated", "tenant_id", "validated"),
        Index("idx_matches_confidence", "confidence"),
    )


class BankTransactionModel(Base):
    """Bank statement transactions imported from OFX."""

    __tablename__ = "bank_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bank_account_id = Column(String(64), nullable=False, index=True)
    bank_transaction_id = Column(String(120), index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(20), nullable=False)
    memo = Column(Text)
    description_user_friendly = Column(Text)
    check_number = Column(String(50))
    is_reconciled = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="bank_transactions")
    reconciliations = relationship(
        "BankReconciliationModel", back_populates="bank_transaction", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "idx_bank_transactions_fitid",
            "tenant_id",
            "bank_account_id",
            "bank_transaction_id",
            unique=True,
        ),
    )


class BankReconciliationModel(Base):
    """Matches between bank transactions and acquirer transactions."""

    __tablename__ = "bank_reconciliations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bank_transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bank_transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    acquirer_transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("acquirer_transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    match_confidence = Column(Numeric(3, 2), nullable=False)
    matched_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("TenantModel", back_populates="bank_reconciliations")
    bank_transaction = relationship("BankTransactionModel", back_populates="reconciliations")
    acquirer_transaction = relationship(
        "TransactionModel", back_populates="bank_reconciliations"
    )

    __table_args__ = (
        Index("idx_bank_reconciliations_tenant", "tenant_id", "matched_at"),
    )


class DivergenceModel(Base):
    """Divergence table model."""

    __tablename__ = "divergences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    divergence_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_matches.id", ondelete="SET NULL"))
    expected_value = Column(Numeric(15, 2))
    actual_value = Column(Numeric(15, 2))
    suggested_action = Column(Text)
    status = Column(String(20), default="open", index=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    notes = Column(Text)

    tenant = relationship("TenantModel", back_populates="divergences")
    match = relationship("MatchModel", back_populates="divergences")

    __table_args__ = (
        Index("idx_divergences_tenant_status", "tenant_id", "status"),
        Index("idx_divergences_tenant_severity", "tenant_id", "severity"),
        Index("idx_divergences_detected_at", "detected_at"),
    )


class SettlementModel(Base):
    """Settlement table model."""

    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("acquirer_transactions.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    expected_date = Column(Date, nullable=False, index=True)
    actual_date = Column(Date)
    net_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("TransactionModel", back_populates="settlement")

    __table_args__ = (
        Index("idx_settlements_tenant_status", "tenant_id", "status"),
        Index("idx_settlements_expected_date", "expected_date"),
    )


class UserModel(Base):
    """Application user model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    roles = Column(JSONB, nullable=False, server_default=text("'[\"user\"]'::jsonb"))
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    tenant = relationship("TenantModel", back_populates="users")

    __table_args__ = (
        Index("idx_users_tenant_email", "tenant_id", "email"),
        Index("idx_users_is_active", "is_active"),
    )


class ImportScheduleModel(Base):
    """Model storing automated acquirer import configurations."""

    __tablename__ = "import_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    acquirer = Column(String(50), nullable=False)
    schedule_type = Column(String(20), nullable=False)
    time_of_day = Column(String(5), nullable=False)
    days_to_import = Column(Integer, nullable=False, default=1)
    credential_hint = Column(String(120))
    webhook_url = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("TenantModel")

    __table_args__ = (
        Index("idx_import_schedules_tenant", "tenant_id"),
        Index("idx_import_schedules_active", "tenant_id", "is_active"),
    )


class NotificationModel(Base):
    """Notifications delivered to tenants."""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="info")
    action_url = Column(String(500))
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime)

    tenant = relationship("TenantModel", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_tenant_created", "tenant_id", "created_at"),
        Index("idx_notifications_unread", "tenant_id", "is_read"),
    )


class AlertHistoryModel(Base):
    """Keep track of alerts already triggered to avoid duplicates."""

    __tablename__ = "alert_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id = Column(String(50), nullable=False, index=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    alert_data = Column(JSONB)

    tenant = relationship("TenantModel")

    __table_args__ = (
        Index("idx_alert_history_tenant", "tenant_id", "triggered_at"),
        Index("idx_alert_history_rule", "rule_id", "triggered_at"),
    )
