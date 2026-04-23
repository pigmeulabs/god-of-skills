"""Workspace-level registry persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pigmeu_never_forget.config.defaults import REGISTRY_SCHEMA_SQL
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


@dataclass(slots=True)
class RegistryRecord:
    """Workspace registry row."""

    project_id: str
    project_name: str
    root_path: str
    status: str
    last_seen_at: str


class RegistryStore:
    """Persist discovered projects in the workspace registry."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def initialize(self) -> None:
        """Ensure the registry schema exists."""
        with sqlite_cursor(self._db_path) as connection:
            connection.executescript(REGISTRY_SCHEMA_SQL)

    def upsert_project(self, record: RegistryRecord) -> None:
        """Insert or update a project registry row."""
        with sqlite_cursor(self._db_path) as connection:
            connection.executescript(REGISTRY_SCHEMA_SQL)
            connection.execute(
                """
                insert into projects(project_id, project_name, root_path, status, last_seen_at)
                values (?, ?, ?, ?, ?)
                on conflict(project_id) do update set
                  project_name = excluded.project_name,
                  root_path = excluded.root_path,
                  status = excluded.status,
                  last_seen_at = excluded.last_seen_at
                """,
                (
                    record.project_id,
                    record.project_name,
                    record.root_path,
                    record.status,
                    record.last_seen_at,
                ),
            )

    def list_projects(self) -> list[RegistryRecord]:
        """Return all registry rows."""
        with sqlite_cursor(self._db_path) as connection:
            connection.executescript(REGISTRY_SCHEMA_SQL)
            rows = connection.execute(
                "select project_id, project_name, root_path, status, last_seen_at from projects order by project_id"
            ).fetchall()
        return [RegistryRecord(**dict(row)) for row in rows]

    @staticmethod
    def build_record(project_id: str, project_name: str, root_path: str, status: str) -> RegistryRecord:
        """Build a registry record using the current timestamp."""
        return RegistryRecord(
            project_id=project_id,
            project_name=project_name,
            root_path=root_path,
            status=status,
            last_seen_at=datetime.now(tz=timezone.utc).isoformat(),
        )
