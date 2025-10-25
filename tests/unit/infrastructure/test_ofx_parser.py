from __future__ import annotations

from decimal import Decimal

import pytest

from src.infrastructure.bank.ofx_parser import OFXParser


@pytest.mark.parametrize(
    "content,expected_count",
    [
        (
            """
            <OFX>
              <BANKMSGSRSV1>
                <STMTTRNRS>
                  <STMTRS>
                    <BANKTRANLIST>
                      <STMTTRN>
                        <TRNTYPE>DEBIT</TRNTYPE>
                        <DTPOSTED>20240101120000</DTPOSTED>
                        <TRNAMT>-45.50</TRNAMT>
                        <FITID>1</FITID>
                        <MEMO>Tarifa</MEMO>
                      </STMTTRN>
                      <STMTTRN>
                        <TRNTYPE>CREDIT</TRNTYPE>
                        <DTPOSTED>20240102120000</DTPOSTED>
                        <TRNAMT>100.00</TRNAMT>
                        <FITID>2</FITID>
                        <MEMO>Recebimento</MEMO>
                      </STMTTRN>
                    </BANKTRANLIST>
                  </STMTRS>
                </STMTTRNRS>
              </BANKMSGSRSV1>
            </OFX>
            """,
            2,
        ),
        (
            """
            OFXHEADER:100
            <OFX>
            <BANKMSGSRSV1>
            <STMTTRNRS>
            <STMTRS>
            <BANKTRANLIST>
            <STMTTRN>
            <TRNTYPE>:CREDIT
            <DTPOSTED>:20240201120000
            <TRNAMT>:250.00
            <FITID>:3
            <MEMO>:Venda marketplace
            </STMTTRN>
            </BANKTRANLIST>
            </STMTRS>
            </STMTTRNRS>
            </BANKMSGSRSV1>
            </OFX>
            """,
            1,
        ),
    ],
)
def test_ofx_parser_returns_normalised_transactions(content: str, expected_count: int) -> None:
    parser = OFXParser()
    transactions = parser.parse(content)

    assert len(transactions) == expected_count
    first = transactions[0]
    assert "bank_transaction_id" in first
    assert isinstance(first["amount"], Decimal)
    assert "description_user_friendly" in first


def test_ofx_parser_raises_on_empty_content() -> None:
    parser = OFXParser()
    with pytest.raises(ValueError):
        parser.parse("   ")
