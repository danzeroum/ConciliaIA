"""SQLAlchemy models for PostgreSQL."""

from __future__ import annotations

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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .database import Base


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
    matches = relationship("MatchModel", back_populates="tenant", cascade="all, delete-orphan")
    divergences = relationship("DivergenceModel", back_populates="tenant", cascade="all, delete-orphan")

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
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_time = Column(String(8))
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
    settlement = relationship("SettlementModel", back_populates="transaction", uselist=False)

    __table_args__ = (
        Index("idx_transactions_tenant_date", "tenant_id", "transaction_date"),
        Index("idx_transactions_tenant_acquirer", "tenant_id", "acquirer"),
        Index("idx_transactions_nsu_trgm", "nsu", postgresql_using="gin", postgresql_ops={"nsu": "gin_trgm_ops"}),
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
