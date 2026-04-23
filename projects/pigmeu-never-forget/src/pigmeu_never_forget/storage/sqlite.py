"""SQLite utilities used by the foundation services."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def connect_sqlite(db_path: Path) -> sqlite3.Connection:
    """Return a SQLite connection configured for row access."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("pragma foreign_keys = on")
    return connection


@contextmanager
def sqlite_cursor(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with automatic commit/rollback."""
    connection = connect_sqlite(db_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
