"""Job and lock persistence helpers."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from pigmeu_never_forget.domain.enums import ErrorCode, JobStatus, JobType, LockType
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.domain.models import JobRecord, ProjectLock
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class JobService:
    """Persist jobs and manage exclusive project locks."""

    def create_job(
        self,
        db_path: Path,
        project_id: str,
        job_type: JobType,
        trigger_type: str,
        request_payload: dict[str, object] | None = None,
    ) -> JobRecord:
        """Create a queued job record."""
        job = JobRecord(
            job_id=f"job_{uuid4().hex}",
            project_id=project_id,
            job_type=job_type,
            status=JobStatus.QUEUED,
            trigger_type=trigger_type,
            request_payload=request_payload or {},
        )
        with sqlite_cursor(db_path) as connection:
            connection.execute(
                """
                insert into job_runs(job_id, project_id, job_type, status, started_at, heartbeat_at, finished_at, trigger_type, request_json, summary_json, error_json)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.project_id,
                    job.job_type.value,
                    job.status.value,
                    None,
                    None,
                    None,
                    job.trigger_type,
                    json.dumps(job.request_payload),
                    json.dumps(job.summary_payload),
                    None,
                ),
            )
        return job

    def mark_running(self, db_path: Path, job_id: str) -> None:
        """Move a job into running state and set timestamps."""
        now = _utcnow().isoformat()
        with sqlite_cursor(db_path) as connection:
            connection.execute(
                """
                update job_runs
                set status = ?, started_at = coalesce(started_at, ?), heartbeat_at = ?
                where job_id = ?
                """,
                (JobStatus.RUNNING.value, now, now, job_id),
            )

    def heartbeat(self, db_path: Path, job_id: str) -> None:
        """Refresh the heartbeat for a running job."""
        with sqlite_cursor(db_path) as connection:
            connection.execute(
                "update job_runs set heartbeat_at = ? where job_id = ?",
                (_utcnow().isoformat(), job_id),
            )

    def finish_job(
        self,
        db_path: Path,
        job_id: str,
        status: JobStatus,
        summary_payload: dict[str, object] | None = None,
        error_payload: dict[str, object] | None = None,
    ) -> None:
        """Finish a job with summary or error payload."""
        with sqlite_cursor(db_path) as connection:
            connection.execute(
                """
                update job_runs
                set status = ?, heartbeat_at = ?, finished_at = ?, summary_json = ?, error_json = ?
                where job_id = ?
                """,
                (
                    status.value,
                    _utcnow().isoformat(),
                    _utcnow().isoformat(),
                    json.dumps(summary_payload or {}),
                    json.dumps(error_payload) if error_payload is not None else None,
                    job_id,
                ),
            )

    def acquire_lock(
        self,
        db_path: Path,
        project_id: str,
        lock_type: LockType,
        lock_owner: str,
        ttl_seconds: int = 300,
    ) -> ProjectLock:
        """Acquire or renew an exclusive project lock."""
        now = _utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        with sqlite_cursor(db_path) as connection:
            row = connection.execute(
                "select project_id, lock_owner, lock_type, acquired_at, expires_at from project_locks where project_id = ?",
                (project_id,),
            ).fetchone()
            if row is not None:
                current_expiry = datetime.fromisoformat(row["expires_at"])
                if current_expiry > now and row["lock_owner"] != lock_owner:
                    raise AppError(
                        code=ErrorCode.PROJECT_LOCKED,
                        message=f"Project {project_id} is already locked.",
                        retryable=True,
                        details={"project_id": project_id, "lock_owner": row["lock_owner"]},
                    )
                connection.execute("delete from project_locks where project_id = ?", (project_id,))
            connection.execute(
                """
                insert into project_locks(project_id, lock_owner, lock_type, acquired_at, expires_at)
                values (?, ?, ?, ?, ?)
                """,
                (project_id, lock_owner, lock_type.value, now.isoformat(), expires_at.isoformat()),
            )
        return ProjectLock(
            project_id=project_id,
            lock_owner=lock_owner,
            lock_type=lock_type,
            acquired_at=now,
            expires_at=expires_at,
        )

    def release_lock(self, db_path: Path, project_id: str, lock_owner: str) -> None:
        """Release a project lock if owned by the caller."""
        with sqlite_cursor(db_path) as connection:
            connection.execute(
                "delete from project_locks where project_id = ? and lock_owner = ?",
                (project_id, lock_owner),
            )

    def recover_stale_jobs(self, db_path: Path, heartbeat_timeout_seconds: int = 120) -> int:
        """Mark stale running jobs as failed."""
        cutoff = _utcnow() - timedelta(seconds=heartbeat_timeout_seconds)
        with sqlite_cursor(db_path) as connection:
            rows = connection.execute(
                """
                select job_id, heartbeat_at from job_runs
                where status = ?
                """,
                (JobStatus.RUNNING.value,),
            ).fetchall()
            stale_ids = [
                row["job_id"]
                for row in rows
                if row["heartbeat_at"] and datetime.fromisoformat(row["heartbeat_at"]) < cutoff
            ]
            for job_id in stale_ids:
                connection.execute(
                    """
                    update job_runs
                    set status = ?, finished_at = ?, error_json = ?
                    where job_id = ?
                    """,
                    (
                        JobStatus.FAILED.value,
                        _utcnow().isoformat(),
                        json.dumps({"reason": "stale_heartbeat"}),
                        job_id,
                    ),
                )
        return len(stale_ids)
