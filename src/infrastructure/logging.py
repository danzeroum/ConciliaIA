"""Logging helpers using structlog."""

from __future__ import annotations

import logging

import structlog
import structlog.contextvars


def setup_logging(environment: str = "development") -> None:
    """Configure structlog to emit JSON logs suitable for observability stacks."""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            timestamper,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO if environment == "production" else logging.DEBUG
        ),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(level=logging.INFO)


__all__ = ["setup_logging"]
