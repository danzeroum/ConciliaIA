"""Standardized error envelope and request correlation.

Every error response carries a stable ``error_code`` and a ``request_id`` while
preserving the legacy ``detail`` field so existing clients keep working. The
``request_id`` is also exposed on the ``X-Request-ID`` response header for every
request, forming the basis for end-to-end observability (it can later be fed to
structured logs, tracing and process metrics).
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

logger = structlog.get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"

# Map well-known HTTP status codes to stable, machine-readable error codes.
_STATUS_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    429: "rate_limit_exceeded",
    500: "internal_error",
    503: "service_unavailable",
}


def _error_code_for_status(status_code: int) -> str:
    return _STATUS_ERROR_CODES.get(status_code, f"http_{status_code}")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id to ``request.state`` and the response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers.setdefault(REQUEST_ID_HEADER, request_id)
        return response


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = _request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": _error_code_for_status(exc.status_code),
            "request_id": request_id,
        },
        headers={**(exc.headers or {}), REQUEST_ID_HEADER: request_id},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _request_id(request)
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_code": "validation_error",
            "request_id": request_id,
        },
        headers={REQUEST_ID_HEADER: request_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id(request)
    logger.error(
        "unhandled_exception",
        request_id=request_id,
        path=str(request.url.path),
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "internal_error",
            "request_id": request_id,
        },
        headers={REQUEST_ID_HEADER: request_id},
    )


def install_error_handling(app: FastAPI) -> None:
    """Register the request-id middleware and the error handlers on ``app``."""
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


__all__ = [
    "REQUEST_ID_HEADER",
    "RequestContextMiddleware",
    "install_error_handling",
]
