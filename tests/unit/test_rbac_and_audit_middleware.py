"""Unit tests for RBAC enforcement and the audit middleware write path.

These cover two fixes:
* ``require_roles`` must actually reject users without an allowed role (the
  decorator existed but was never exercised by a test before).
* ``AuditMiddleware`` must construct and persist an ``AuditLogModel`` row for
  audited mutations (previously the write path used raw SQL and was untested,
  so a silent no-op would have gone unnoticed).
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api import dependencies as deps
from src.api.dependencies import require_roles
from src.api.middleware.audit_middleware import AuditMiddleware
from src.infrastructure.persistence.models import AuditLogModel

OPERATIONAL_ROLES = ["analyst", "admin", "manager"]


async def test_require_roles_allows_user_with_matching_role():
    guard = require_roles(OPERATIONAL_ROLES)
    user = {"roles": ["analyst"], "tenant_id": "t1"}

    assert await guard(user=user) is user


async def test_require_roles_blocks_user_without_role():
    guard = require_roles(OPERATIONAL_ROLES)
    user = {"roles": ["user"], "tenant_id": "t1"}

    with pytest.raises(HTTPException) as exc_info:
        await guard(user=user)

    assert exc_info.value.status_code == 403


class _FakeSession:
    def __init__(self) -> None:
        self.added: list = []
        self.committed = False

    def add(self, obj) -> None:
        self.added.append(obj)

    async def commit(self) -> None:
        self.committed = True


class _FakeDatabase:
    def __init__(self) -> None:
        self.session = _FakeSession()

    async def get_session(self):
        yield self.session


async def test_audit_middleware_persists_row(monkeypatch):
    fake_db = _FakeDatabase()
    monkeypatch.setattr(deps, "database", fake_db)

    tenant_id = uuid4()
    request = SimpleNamespace(
        state=SimpleNamespace(tenant_id=str(tenant_id), user_id="user-42"),
        headers={"X-Forwarded-For": "203.0.113.7", "User-Agent": "pytest"},
        client=SimpleNamespace(host="203.0.113.7"),
    )

    await AuditMiddleware._write_log(
        request, "/api/v1/divergences/abc-123/resolve", "POST", 200
    )

    assert fake_db.session.committed is True
    assert len(fake_db.session.added) == 1

    row = fake_db.session.added[0]
    assert isinstance(row, AuditLogModel)
    assert row.action == "post:divergences"
    assert row.resource_type == "divergences"
    assert row.resource_id == "abc-123"
    assert row.user_id == "user-42"
    assert row.tenant_id == tenant_id
    assert row.status == "success"
    assert row.ip_address == "203.0.113.7"


async def test_audit_middleware_skips_when_tenant_missing(monkeypatch):
    fake_db = _FakeDatabase()
    monkeypatch.setattr(deps, "database", fake_db)

    request = SimpleNamespace(
        state=SimpleNamespace(tenant_id=None, user_id="user-42"),
        headers={},
        client=None,
    )

    await AuditMiddleware._write_log(request, "/api/v1/reports/accuracy", "POST", 200)

    assert fake_db.session.added == []
    assert fake_db.session.committed is False
