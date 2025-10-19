"""Health check endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    tags=["Health"],
)
async def health_check() -> dict[str, str]:
    """Return a simple payload for uptime monitors."""

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "conciliaai-api",
    }
