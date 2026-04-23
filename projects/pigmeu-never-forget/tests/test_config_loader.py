from __future__ import annotations

from pathlib import Path

import pytest

from pigmeu_never_forget.config.loader import build_workspace_paths, load_workspace_settings
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.utils.yaml_compat import safe_dump


def test_load_workspace_settings_uses_defaults_without_file() -> None:
    settings = load_workspace_settings()
    assert settings["workspace"]["project_dir_mode"] == "immediate_children"
    assert settings["storage"]["collection_prefix"] == "kb_"


def test_load_workspace_settings_merges_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "workspace": {"root_path": "./workspace-root"},
                "storage": {"collection_prefix": "custom_"},
            }
        ),
        encoding="utf-8",
    )

    settings = load_workspace_settings(str(config_path))
    assert settings["workspace"]["root_path"] == "./workspace-root"
    assert settings["storage"]["collection_prefix"] == "custom_"
    assert settings["retrieval"]["top_k"] == 8


def test_load_workspace_settings_rejects_non_mapping(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(safe_dump(["not", "a", "mapping"]), encoding="utf-8")

    with pytest.raises(AppError):
        load_workspace_settings(str(config_path))


def test_build_workspace_paths_resolves_metadata(tmp_path: Path) -> None:
    settings = load_workspace_settings()
    settings["workspace"]["root_path"] = str(tmp_path / "workspace")
    paths = build_workspace_paths(settings)
    assert paths.metadata_path == tmp_path / "workspace" / "_workspace"
