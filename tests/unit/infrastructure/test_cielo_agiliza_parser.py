from datetime import date
from decimal import Decimal

import pytest

from src.infrastructure.acquirers import CieloAgilizaParser


def test_parse_agiliza_csv_generates_transactions():
    csv_content = (
        "NSU;Data Transação;Hora;Data Pagamento;Valor Bruto;Valor Líquido;"
        "Taxa MDR (%);Bandeira;Últimos 4;Autorização;Total Parcelas;Parcela Atual;Status\n"
        "123456;01/03/2024;13:45;05/03/2024;1.234,56;1.200,00;2,80%;Visa;1234;A1B2C3;2;1;Aprovada\n"
    )

    parser = CieloAgilizaParser()

    transactions = parser.parse(csv_content, tenant_id="tenant-123")

    assert len(transactions) == 1
    transaction = transactions[0]

    assert transaction.tenant_id == "tenant-123"
    assert transaction.nsu.value == "123456"
    assert transaction.transaction_date == date(2024, 3, 1)
    assert transaction.settlement_date == date(2024, 3, 5)
    assert transaction.transaction_time and transaction.transaction_time.hour == 13
    assert transaction.transaction_time.minute == 45
    assert transaction.card_brand == "visa"
    assert transaction.card_last_4 == "1234"
    assert transaction.amount.amount == Decimal("1234.56")
    assert transaction.net_amount and transaction.net_amount.amount == Decimal("1200.00")
    assert transaction.mdr_amount and transaction.mdr_amount.amount == Decimal("34.56")
    assert transaction.mdr_rate and transaction.mdr_rate.value == Decimal("0.0280")
    assert transaction.status.value == "approved"
    assert transaction.installment_plan
    assert transaction.installment_plan.total_installments == 2
    assert transaction.installment_plan.current_installment == 1


@pytest.mark.parametrize(
    "csv_content",
    [
        "",
        "NSU;Data Transação;Valor Bruto\n;;\n",
        "NSU;Data Transação;Valor Bruto\n123;32/13/2024;0,00\n",
    ],
)
def test_invalid_rows_are_ignored(csv_content: str):
    parser = CieloAgilizaParser()
    transactions = parser.parse(csv_content, tenant_id="tenant-xyz")
    assert transactions == []
