"""Authorization code value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationCode:
    """Represents an authorization code emitted by the card network."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Authorization code cannot be empty")

        normalized = "".join(char.upper() for char in self.value if char.isalnum())
        if len(normalized) < 4 or len(normalized) > 10:
            raise ValueError("Authorization code must have between 4 and 10 characters")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value
