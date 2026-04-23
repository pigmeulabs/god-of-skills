"""Application-specific error types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pigmeu_never_forget.domain.enums import ErrorCode


@dataclass(slots=True)
class AppError(Exception):
    """Structured application error."""

    code: ErrorCode
    message: str
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return the public error envelope payload."""
        return {
            "code": self.code.value,
            "message": self.message,
            "retryable": self.retryable,
            "details": self.details,
        }
