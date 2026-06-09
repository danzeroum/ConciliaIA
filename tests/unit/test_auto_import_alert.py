"""Unit tests for the auto-import failure webhook alert.

Wires up the previously-dead ``webhook_url`` field: on a failed scheduled
import the scheduler now POSTs a best-effort alert to the configured webhook.
"""

from __future__ import annotations

from types import SimpleNamespace

from src.infrastructure.scheduler import auto_import as auto_import_module
from src.infrastructure.scheduler.auto_import import AutoImportScheduler


def _scheduler() -> AutoImportScheduler:
    async def _runner(_schedule):  # pragma: no cover - not invoked in these tests
        return None

    return AutoImportScheduler(session_factory=lambda: None, runner=_runner)


async def test_notify_failure_posts_to_configured_webhook(monkeypatch):
    captured = []

    async def fake_post(url, payload):
        captured.append((url, payload))
        return 200

    monkeypatch.setattr(auto_import_module, "_post_webhook", fake_post)

    schedule = SimpleNamespace(
        id="sched-1",
        tenant_id="tenant-1",
        acquirer="cielo",
        webhook_url="https://hook.example/alert",
    )
    await _scheduler()._notify_failure(schedule, "boom")

    assert len(captured) == 1
    url, payload = captured[0]
    assert url == "https://hook.example/alert"
    assert payload["event"] == "auto_import_failed"
    assert payload["schedule_id"] == "sched-1"
    assert payload["tenant_id"] == "tenant-1"
    assert payload["error"] == "boom"


async def test_notify_failure_is_noop_without_webhook(monkeypatch):
    captured = []

    async def fake_post(url, payload):
        captured.append((url, payload))
        return 200

    monkeypatch.setattr(auto_import_module, "_post_webhook", fake_post)

    schedule = SimpleNamespace(
        id="sched-1", tenant_id="tenant-1", acquirer="cielo", webhook_url=None
    )
    await _scheduler()._notify_failure(schedule, "boom")

    assert captured == []


async def test_notify_failure_swallows_webhook_errors(monkeypatch):
    async def boom_post(url, payload):
        raise RuntimeError("network down")

    monkeypatch.setattr(auto_import_module, "_post_webhook", boom_post)

    schedule = SimpleNamespace(
        id="s", tenant_id="t", acquirer="cielo", webhook_url="https://hook"
    )
    # Must not raise — alert failures are logged, never propagated.
    await _scheduler()._notify_failure(schedule, "boom")
