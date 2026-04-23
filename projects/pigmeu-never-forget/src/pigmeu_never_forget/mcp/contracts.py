"""Shared MCP contracts and adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigmeu_never_forget.domain.enums import ErrorCode
from pigmeu_never_forget.domain.errors import AppError


@dataclass(slots=True)
class MCPResult:
    """Standardized MCP tool result envelope."""

    status: str
    data: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"status": self.status}
        if self.data is not None:
            payload["data"] = self.data
        if self.error is not None:
            payload["error"] = self.error
        if self.meta is not None:
            payload["meta"] = self.meta
        return payload


def success(
    data: dict[str, Any],
    *,
    project_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if project_id:
        meta["project_id"] = project_id
    if request_id:
        meta["request_id"] = request_id
    return MCPResult(
        status="ok",
        data=data,
        meta=meta or None,
    ).to_dict()


def error_from_exception(
    exc: Exception,
    *,
    request_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(exc, AppError):
        error = exc.to_dict()
    elif isinstance(exc, FileNotFoundError):
        error = AppError(
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=str(exc),
            retryable=False,
            details={},
        ).to_dict()
    else:
        error = AppError(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(exc) or "Unexpected MCP error.",
            retryable=False,
            details={},
        ).to_dict()
    meta = {"request_id": request_id} if request_id else None
    return MCPResult(
        status="error",
        error=error,
        meta=meta,
    ).to_dict()

