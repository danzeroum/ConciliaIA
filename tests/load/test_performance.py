"""Load tests using Locust to simulate tenants executing reconciliation."""

from __future__ import annotations

import pytest
from locust import HttpUser, between, task


class ReconciliationUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "test-tenant", "password": "test-password"},
        )
        payload = response.json()
        self.token = payload.get("access_token", "")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def reconcile_transactions(self) -> None:
        payload = {"start_date": "2025-01-01", "end_date": "2025-01-31"}

        with self.client.post(
            "/api/v1/reconciliation/execute",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "matched" in result and "accuracy" in result:
                    response.success()
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(2)
    def get_divergences(self) -> None:
        self.client.get(
            "/api/v1/divergences?status=open",
            headers=self.headers,
            name="/api/v1/divergences",
        )

    @task(1)
    def get_matches(self) -> None:
        self.client.get(
            "/api/v1/matches?limit=100",
            headers=self.headers,
            name="/api/v1/matches",
        )


@pytest.mark.load
class TestPerformance:
    @pytest.mark.skip("Executar manualmente com Locust")
    def test_load_scenario_phase2(self) -> None:
        pass
