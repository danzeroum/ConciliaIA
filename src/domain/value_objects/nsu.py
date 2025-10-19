"""NSU (Número Sequencial Único) value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NSU:
    """Número Sequencial Único da transação na adquirente."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("NSU cannot be empty")

        normalized = self.value.strip().upper()
        if len(normalized) < 6 or len(normalized) > 20:
            raise ValueError("NSU length must be between 6 and 20 characters")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value

    def __hash__(self) -> int:  # pragma: no cover - trivial
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NSU):
            return NotImplemented
        return self.value == other.value
