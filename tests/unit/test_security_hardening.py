"""Unit tests for the security-hardening primitives.

Covers the in-process login lockout (brute-force mitigation) and the JWT
``jti`` blocklist (logout revocation + refresh-token rotation/reuse detection).
"""

from __future__ import annotations

import time

from src.infrastructure.security import LoginAttemptTracker, TokenBlocklist


def test_login_lockout_after_max_attempts():
    tracker = LoginAttemptTracker(max_attempts=3, lockout_seconds=900)
    key = "user@example.com"

    assert tracker.seconds_until_unlock(key) == 0
    assert tracker.register_failure(key) == 0  # attempt 1
    assert tracker.register_failure(key) == 0  # attempt 2
    assert tracker.register_failure(key) == 900  # attempt 3 -> locked
    assert tracker.seconds_until_unlock(key) > 0


def test_login_reset_clears_lock():
    tracker = LoginAttemptTracker(max_attempts=2, lockout_seconds=900)
    key = "a@b.com"

    tracker.register_failure(key)
    tracker.register_failure(key)
    assert tracker.seconds_until_unlock(key) > 0

    tracker.reset(key)
    assert tracker.seconds_until_unlock(key) == 0


def test_login_lockout_expires():
    tracker = LoginAttemptTracker(max_attempts=1, lockout_seconds=900)
    key = "c@d.com"

    tracker.register_failure(key)  # locked immediately
    assert tracker.seconds_until_unlock(key) > 0

    # Force the lock into the past — it must auto-clear.
    tracker._locked_until[key] = time.monotonic() - 1
    assert tracker.seconds_until_unlock(key) == 0


def test_token_blocklist_revoke_and_check():
    bl = TokenBlocklist()
    assert bl.is_revoked("jti-1") is False
    bl.revoke("jti-1", 900)
    assert bl.is_revoked("jti-1") is True


def test_token_blocklist_ignores_falsy_and_nonpositive_ttl():
    bl = TokenBlocklist()
    bl.revoke(None, 900)
    bl.revoke("jti-x", 0)
    bl.revoke("jti-y", -5)

    assert bl.is_revoked(None) is False
    assert bl.is_revoked("jti-x") is False
    assert bl.is_revoked("jti-y") is False


def test_token_blocklist_expiry():
    bl = TokenBlocklist()
    bl.revoke("jti-exp", 900)
    assert bl.is_revoked("jti-exp") is True

    # Force expiry into the past — is_revoked must return False and purge it.
    bl._revoked["jti-exp"] = time.monotonic() - 1
    assert bl.is_revoked("jti-exp") is False
