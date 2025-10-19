"""Load testing with Locust."""

from __future__ import annotations

from locust import HttpUser, between, task


class ConciliaAIUser(HttpUser):
    """Simulated user for load testing."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        """Login before starting tasks."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
        else:
            self.access_token = None

    @task(3)
    def health_check(self) -> None:
        """Health check endpoint (most frequent)."""
        self.client.get("/health")

    @task(1)
    def get_sales(self) -> None:
        """Get sales (authenticated)."""
        if self.access_token:
            self.client.get(
                "/api/v1/matches",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
