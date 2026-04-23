"""Shared enums used across the project foundation."""

from __future__ import annotations

from enum import StrEnum


class JobType(StrEnum):
    """Supported job types."""

    DISCOVER = "discover"
    SYNC = "sync"
    INDEX = "index"
    QUERY = "query"
    CONSOLIDATE = "consolidate"


class JobStatus(StrEnum):
    """Lifecycle states for jobs."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LockType(StrEnum):
    """Project-level exclusive lock types."""

    SYNC = "sync"
    CONSOLIDATE = "consolidate"


class ErrorCode(StrEnum):
    """Public error codes aligned with the docs."""

    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_LOCKED = "PROJECT_LOCKED"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    INVALID_REQUEST = "INVALID_REQUEST"
    PARSER_ERROR = "PARSER_ERROR"
    PROVIDER_RATE_LIMITED = "PROVIDER_RATE_LIMITED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    VECTOR_STORE_ERROR = "VECTOR_STORE_ERROR"
    CONSOLIDATION_CONFLICT = "CONSOLIDATION_CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class DocumentStatus(StrEnum):
    """Statuses used for document persistence."""

    ACTIVE = "active"
    DELETED = "deleted"
    ERROR = "error"
