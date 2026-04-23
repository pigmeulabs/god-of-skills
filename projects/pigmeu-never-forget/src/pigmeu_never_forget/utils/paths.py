"""Path and naming helpers."""

from __future__ import annotations

import re
from pathlib import Path


def ensure_absolute_path(path: Path, base_dir: Path | None = None) -> Path:
    """Resolve a path against a base directory if needed."""
    if path.is_absolute():
        return path.resolve()
    if base_dir is not None:
        return (base_dir / path).resolve()
    return path.resolve()


def slugify(value: str) -> str:
    """Convert a string into a filesystem and collection safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "project"
