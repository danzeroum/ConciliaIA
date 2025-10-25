"""Mappers to convert between domain entities and database models."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from src.domain.entities import (
    AcquirerTransaction,
    BankReconciliation,
    BankTransaction,
    Divergence,
    DivergenceStatus,
    DivergenceType,
    ImportSchedule,
    Notification,
    MatchType,
    ReconciliationMatch,
    Sale,
    Settlement,
    SettlementStatus,
    Severity,
    Tenant,
    TransactionStatus,
)
from src.domain.value_objects import Money, Percentage
from .models import (
    BankReconciliationModel,
    BankTransactionModel,
    DivergenceModel,
    ImportScheduleModel,
    NotificationModel,
    MatchModel,
    SaleModel,
    SettlementModel,
    TenantModel,
    TransactionModel,
)


class TenantMapper:
    """Map between Tenant entity and TenantModel."""

    @staticmethod
    def to_entity(model: TenantModel) -> Tenant:
        """Convert model to entity."""
        return Tenant(
            id=str(model.id),
            org_name=model.org_name,
            cnpj=model.cnpj,
            tier=model.tier,
            active=model.active,
            features=model.features or [],
            rate_limit=model.rate_limit,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Tenant, model: Optional[TenantModel] = None) -> TenantModel:
        """Convert entity to model."""
        if model is None:
            model = TenantModel()

        model.id = entity.id
        model.org_name = entity.org_name
        model.cnpj = entity.cnpj
        model.tier = entity.tier.value if hasattr(entity.tier, "value") else entity.tier
        model.active = entity.active
        model.features = entity.features
        model.rate_limit = entity.rate_limit
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model


class SaleMapper:
    """Map between Sale entity and SaleModel."""

    @staticmethod
    def to_entity(model: SaleModel) -> Sale:
        """Convert model to entity."""
        return Sale(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            nsu=model.nsu,
            amount=Money(Decimal(model.amount), model.currency),
            date=model.date,
            payment_method=model.payment_method,
            authorization_code=model.authorization_code,
            installments=model.installments,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Sale, model: Optional[SaleModel] = None) -> SaleModel:
        """Convert entity to model."""
        if model is None:
            model = SaleModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.nsu = str(entity.nsu)
        model.amount = entity.amount.amount
        model.currency = entity.amount.currency
        model.date = entity.date
        model.payment_method = entity.payment_method
        model.authorization_code = (
            str(entity.authorization_code) if getattr(entity, "authorization_code", None) else None
        )
        model.installments = entity.installments
        model.created_at = entity.created_at

        return model


class TransactionMapper:
    """Map between AcquirerTransaction entity and TransactionModel."""

    @staticmethod
    def to_entity(model: TransactionModel) -> AcquirerTransaction:
        """Convert model to entity."""
        mdr_rate = Percentage(Decimal(model.mdr_rate)) if model.mdr_rate is not None else None
        mdr_amount = Money(Decimal(model.mdr_amount), model.currency) if model.mdr_amount is not None else None
        net_amount = Money(Decimal(model.net_amount), model.currency) if model.net_amount is not None else None

        return AcquirerTransaction(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            acquirer=model.acquirer,
            nsu=model.nsu,
            amount=Money(Decimal(model.amount), model.currency),
            transaction_date=model.transaction_date,
            settlement_date=model.settlement_date,
            authorization_code=model.authorization_code,
            card_brand=model.card_brand,
            card_last_4=model.card_last_4,
            mdr_rate=mdr_rate,
            mdr_amount=mdr_amount,
            net_amount=net_amount,
            status=TransactionStatus(model.status),
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: AcquirerTransaction, model: Optional[TransactionModel] = None) -> TransactionModel:
        """Convert entity to model."""
        if model is None:
            model = TransactionModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.acquirer = entity.acquirer.value if hasattr(entity.acquirer, "value") else str(entity.acquirer)
        model.nsu = str(entity.nsu)
        model.amount = entity.amount.amount
        model.currency = entity.amount.currency
        model.transaction_date = entity.transaction_date
        model.settlement_date = entity.settlement_date
        model.authorization_code = (
            str(entity.authorization_code) if getattr(entity, "authorization_code", None) else None
        )
        model.card_brand = entity.card_brand
        model.card_last_4 = entity.card_last_4
        model.mdr_rate = entity.mdr_rate.value if entity.mdr_rate else None
        model.mdr_amount = entity.mdr_amount.amount if entity.mdr_amount else None
        model.net_amount = entity.net_amount.amount if entity.net_amount else None
        model.status = entity.status.value if hasattr(entity.status, "value") else entity.status
        model.created_at = entity.created_at

        return model


class NotificationMapper:
    """Map between Notification entity and NotificationModel."""

    @staticmethod
    def to_entity(model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            tenant_id=str(model.tenant_id),
            title=model.title,
            message=model.message,
            priority=model.priority,
            action_url=model.action_url,
            is_read=model.is_read,
            created_at=model.created_at,
            read_at=model.read_at,
        )

    @staticmethod
    def to_model(entity: Notification, model: Optional[NotificationModel] = None) -> NotificationModel:
        if model is None:
            model = NotificationModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.title = entity.title
        model.message = entity.message
        model.priority = entity.priority
        model.action_url = entity.action_url
        model.is_read = entity.is_read
        model.created_at = entity.created_at
        model.read_at = entity.read_at

        return model


class MatchMapper:
    """Map between ReconciliationMatch entity and MatchModel."""

    @staticmethod
    def to_entity(model: MatchModel) -> ReconciliationMatch:
        """Convert model to entity."""
        return ReconciliationMatch(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            sale_id=str(model.sale_id),
            transaction_id=str(model.transaction_id),
            match_type=MatchType(model.match_type),
            confidence=Decimal(model.confidence),
            validated=model.validated,
            validated_by=model.validated_by,
            validated_at=model.validated_at,
            matched_at=model.matched_at,
        )

    @staticmethod
    def to_model(entity: ReconciliationMatch, model: Optional[MatchModel] = None) -> MatchModel:
        """Convert entity to model."""
        if model is None:
            model = MatchModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.sale_id = entity.sale_id
        model.transaction_id = entity.transaction_id
        model.match_type = entity.match_type.value if hasattr(entity.match_type, "value") else entity.match_type
        model.confidence = entity.confidence
        model.validated = entity.validated
        model.validated_by = entity.validated_by
        model.validated_at = entity.validated_at
        model.matched_at = entity.matched_at

        return model


class BankTransactionMapper:
    """Map bank transactions between domain and persistence models."""

    @staticmethod
    def to_entity(model: BankTransactionModel) -> BankTransaction:
        return BankTransaction(
            id=model.id,
            tenant_id=str(model.tenant_id),
            bank_account_id=model.bank_account_id,
            bank_transaction_id=model.bank_transaction_id or "",
            transaction_date=model.transaction_date,
            amount=Decimal(model.amount),
            type=model.type,
            memo=model.memo or "",
            description_user_friendly=model.description_user_friendly or "",
            check_number=model.check_number or "",
            is_reconciled=model.is_reconciled,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(
        entity: BankTransaction, model: BankTransactionModel | None = None
    ) -> BankTransactionModel:
        if model is None:
            model = BankTransactionModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.bank_account_id = entity.bank_account_id
        model.bank_transaction_id = entity.bank_transaction_id
        model.transaction_date = entity.transaction_date
        model.amount = entity.amount
        model.type = entity.type
        model.memo = entity.memo
        model.description_user_friendly = entity.description_user_friendly
        model.check_number = entity.check_number
        model.is_reconciled = entity.is_reconciled
        model.created_at = entity.created_at

        return model


class BankReconciliationMapper:
    """Map reconciliation links between domain entity and persistence model."""

    @staticmethod
    def to_entity(model: BankReconciliationModel) -> BankReconciliation:
        return BankReconciliation(
            id=model.id,
            tenant_id=str(model.tenant_id),
            bank_transaction_id=model.bank_transaction_id,
            acquirer_transaction_id=str(model.acquirer_transaction_id),
            match_confidence=float(model.match_confidence),
            matched_at=model.matched_at,
        )

    @staticmethod
    def to_model(
        entity: BankReconciliation,
        model: BankReconciliationModel | None = None,
    ) -> BankReconciliationModel:
        if model is None:
            model = BankReconciliationModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.bank_transaction_id = entity.bank_transaction_id
        model.acquirer_transaction_id = entity.acquirer_transaction_id
        model.match_confidence = entity.match_confidence
        model.matched_at = entity.matched_at

        return model


class DivergenceMapper:
    """Map between Divergence entity and DivergenceModel."""

    @staticmethod
    def to_entity(model: DivergenceModel) -> Divergence:
        """Convert model to entity."""
        expected_value = Money(Decimal(model.expected_value)) if model.expected_value is not None else None
        actual_value = Money(Decimal(model.actual_value)) if model.actual_value is not None else None

        return Divergence(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            divergence_type=DivergenceType(model.divergence_type),
            severity=Severity(model.severity),
            match_id=str(model.match_id) if model.match_id else None,
            expected_value=expected_value,
            actual_value=actual_value,
            suggested_action=model.suggested_action,
            status=DivergenceStatus(model.status),
            detected_at=model.detected_at,
            resolved_at=model.resolved_at,
            resolved_by=model.resolved_by,
            notes=model.notes,
        )

    @staticmethod
    def to_model(entity: Divergence, model: Optional[DivergenceModel] = None) -> DivergenceModel:
        """Convert entity to model."""
        if model is None:
            model = DivergenceModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.divergence_type = (
            entity.divergence_type.value if hasattr(entity.divergence_type, "value") else entity.divergence_type
        )
        model.severity = entity.severity.value if hasattr(entity.severity, "value") else entity.severity
        model.match_id = entity.match_id
        model.expected_value = entity.expected_value.amount if entity.expected_value else None
        model.actual_value = entity.actual_value.amount if entity.actual_value else None
        model.suggested_action = entity.suggested_action
        model.status = entity.status.value if hasattr(entity.status, "value") else entity.status
        model.detected_at = entity.detected_at
        model.resolved_at = entity.resolved_at
        model.resolved_by = entity.resolved_by
        model.notes = entity.notes

        return model


class SettlementMapper:
    """Map between Settlement entity and SettlementModel."""

    @staticmethod
    def to_entity(model: SettlementModel) -> Settlement:
        """Convert model to entity."""
        return Settlement(
            id=str(model.id),
            transaction_id=str(model.transaction_id),
            tenant_id=str(model.tenant_id),
            expected_date=model.expected_date,
            net_amount=Money(Decimal(model.net_amount)),
            actual_date=model.actual_date,
            status=SettlementStatus(model.status),
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Settlement, model: Optional[SettlementModel] = None) -> SettlementModel:
        """Convert entity to model."""
        if model is None:
            model = SettlementModel()

        model.id = entity.id
        model.transaction_id = entity.transaction_id
        model.tenant_id = entity.tenant_id
        model.expected_date = entity.expected_date
        model.net_amount = entity.net_amount.amount
        model.actual_date = entity.actual_date
        model.status = entity.status.value if hasattr(entity.status, "value") else entity.status
        model.created_at = entity.created_at

        return model


class ImportScheduleMapper:
    """Map between ImportSchedule entity and ImportScheduleModel."""

    @staticmethod
    def to_entity(model: ImportScheduleModel) -> ImportSchedule:
        return ImportSchedule(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            acquirer=model.acquirer,
            schedule_type=model.schedule_type,
            time_of_day=model.time_of_day,
            days_to_import=model.days_to_import,
            credential_hint=model.credential_hint,
            webhook_url=model.webhook_url,
            is_active=model.is_active,
            last_run_at=model.last_run_at,
            next_run_at=model.next_run_at,
            error_count=model.error_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(
        entity: ImportSchedule, model: ImportScheduleModel | None = None
    ) -> ImportScheduleModel:
        if model is None:
            model = ImportScheduleModel()

        model.id = entity.id
        model.tenant_id = entity.tenant_id
        model.acquirer = entity.acquirer
        model.schedule_type = entity.schedule_type
        model.time_of_day = entity.time_of_day
        model.days_to_import = entity.days_to_import
        model.credential_hint = entity.credential_hint
        model.webhook_url = entity.webhook_url
        model.is_active = entity.is_active
        model.last_run_at = entity.last_run_at
        model.next_run_at = entity.next_run_at
        model.error_count = entity.error_count
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model
