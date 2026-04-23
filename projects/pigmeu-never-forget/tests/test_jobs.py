from __future__ import annotations

from pathlib import Path

import pytest

from pigmeu_never_forget.domain.enums import ErrorCode, LockType
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.storage.migrations import STATE_MIGRATIONS, apply_migrations


def test_project_lock_is_exclusive(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    apply_migrations(db_path, STATE_MIGRATIONS)
    service = JobService()

    service.acquire_lock(
        db_path=db_path,
        project_id="project-a",
        lock_type=LockType.SYNC,
        lock_owner="job-1",
    )

    with pytest.raises(AppError) as exc:
        service.acquire_lock(
            db_path=db_path,
            project_id="project-a",
            lock_type=LockType.CONSOLIDATE,
            lock_owner="job-2",
        )

    assert exc.value.code == ErrorCode.PROJECT_LOCKED
