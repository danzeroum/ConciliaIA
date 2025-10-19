"""Load and stress testing scenarios for ConciliaAI."""

from __future__ import annotations

import random
from datetime import date, timedelta

from locust import FastHttpUser, HttpUser, between, events, task


class ConciliaAIUser(FastHttpUser):
    """Simulates the regular behaviour of a ConciliaAI tenant."""

    wait_time = between(1, 5)

    def on_start(self) -> None:
        username = f"tenant-{random.randint(1, 50)}"
        password = "test-password"
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
            name="/api/v1/auth/login",
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.headers = {"Authorization": f"Bearer {token}"}
                return
        self.headers = {}

    @task(7)
    def reconcile_transactions(self) -> None:
        if not getattr(self, "headers", None):
            return

        end_date = date.today()
        start_date = end_date - timedelta(days=random.randint(7, 30))
        payload = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "auto_approve": True,
        }

        with self.client.post(
            "/api/v1/reconciliation/execute",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/api/v1/reconciliation/execute",
        ) as response:
            if response.status_code == 200:
                body = response.json()
                if "matched" in body and "accuracy" in body:
                    accuracy = body["accuracy"]
                    events.request.fire(
                        request_type="METRIC",
                        name="matching_accuracy",
                        response_time=0,
                        response_length=0,
                        context={"accuracy": accuracy},
                    )
                    response.success()
                else:
                    response.failure("Invalid response structure")
            elif response.status_code == 429:
                response.failure("Rate limit exceeded")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def get_divergences(self) -> None:
        if not getattr(self, "headers", None):
            return
        self.client.get(
            "/api/v1/divergences?status=open&limit=50",
            headers=self.headers,
            name="/api/v1/divergences",
        )

    @task(1)
    def get_matches(self) -> None:
        if not getattr(self, "headers", None):
            return
        self.client.get(
            "/api/v1/matches?limit=100",
            headers=self.headers,
            name="/api/v1/matches",
        )


class StressTestUser(FastHttpUser):
    """Aggressive workload used to simulate high pressure scenarios."""

    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        self.headers = {}

    @task
    def heavy_reconciliation(self) -> None:
        if not getattr(self, "headers", None):
            return

        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        payload = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "auto_approve": True,
        }
        self.client.post(
            "/api/v1/reconciliation/execute",
            json=payload,
            headers=self.headers,
            name="/api/v1/reconciliation/execute [HEAVY]",
        )


@events.init.add_listener
def on_locust_init(environment, **kwargs):  # pragma: no cover - executed during locust runs
    environment.accuracy_samples = []


@events.request.add_listener
def on_request(
    request_type,
    name,
    response_time,
    response_length,
    exception,
    context,
    **kwargs,
):  # pragma: no cover - executed during locust runs
    if request_type == "METRIC" and name == "matching_accuracy":
        accuracy = context.get("accuracy", 0)
        print(f"Matching Accuracy Sample: {accuracy:.2f}%")


class LoadTestScenario(HttpUser):  # pragma: no cover - documentation helper
    wait_time = between(1, 1)

    @task
    def noop(self) -> None:
        pass
