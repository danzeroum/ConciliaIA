"""Regression test for the dashboard stats response model.

GET /api/v1/stats/dashboard returned 500 whenever there were transactions or
unresolved divergences: the response fields were typed ``List[Dict[str, int]]``
/ ``List[Dict[str, float | int]]``, so the string ``acquirer``/``type`` labels
failed numeric validation. The fields are now typed sub-models; this test pins
that the real label+number shapes validate.
"""

from __future__ import annotations

from src.api.v1.routes.stats import (
    DashboardStatsResponse,
    KPIMetrics,
    TrendDataPoint,
)


def _kpis() -> KPIMetrics:
    return KPIMetrics(
        accuracy=95.0,
        total_matches=95,
        pending_divergences=3,
        resolved_today=0,
        total_sales=100,
        total_transactions=95,
        total_amount_reconciled=54150.0,
    )


def test_dashboard_response_accepts_label_and_number_dicts():
    response = DashboardStatsResponse(
        kpis=_kpis(),
        accuracy_trend=[TrendDataPoint(date="2026-06-09", value=95.0)],
        top_divergence_types=[{"type": "missing_transaction", "count": 3}],
        acquirer_breakdown=[
            {"acquirer": "cielo", "transactions": 50, "amount": 25000.0},
            {"acquirer": "rede", "transactions": 45, "amount": 29150.0},
        ],
    )

    assert response.acquirer_breakdown[0].acquirer == "cielo"
    assert response.acquirer_breakdown[0].transactions == 50
    assert response.top_divergence_types[0].type == "missing_transaction"
    assert response.top_divergence_types[0].count == 3
