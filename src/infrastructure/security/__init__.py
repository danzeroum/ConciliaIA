"""Security helpers used by infrastructure components."""

from __future__ import annotations

from typing import Dict


class SecretsManager:
    """Abstraction over the secrets manager used to retrieve credentials."""

    async def get_acquirer_credentials(self, tenant_id: str, acquirer: str) -> Dict[str, str]:
        raise NotImplementedError


__all__ = ["SecretsManager"]
