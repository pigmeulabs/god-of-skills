from __future__ import annotations

from pathlib import Path

import pytest

from pigmeu_never_forget.utils.yaml_compat import safe_dump


pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from pigmeu_never_forget.http.api import create_http_app  # noqa: E402


def test_http_api_flow(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "auth.md").write_text("# Auth\nRefresh token flow.\n", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "workspace": {
                    "root_path": str(workspace_root),
                    "project_dir_mode": "immediate_children",
                    "ignore_dirs": ["_workspace", ".git"],
                },
                "storage": {"collection_prefix": "kb_"},
            }
        ),
        encoding="utf-8",
    )

    app = create_http_app(str(config_path))
    client = TestClient(app)

    health = client.get("/health", headers={"X-Request-Id": "req-health"})
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["meta"]["request_id"] == "req-health"

    discovered = client.post("/projects/discover", headers={"X-Request-Id": "req-discover"})
    assert discovered.status_code == 200
    assert discovered.json()["status"] == "ok"

    sync = client.post("/projects/project-a/sync", json={})
    assert sync.status_code == 200
    assert sync.json()["status"] == "ok"

    search = client.post(
        "/projects/project-a/search",
        json={"query": "refresh token", "top_k": 3},
    )
    assert search.status_code == 200
    assert search.json()["status"] == "ok"
    assert isinstance(search.json()["data"]["hits"], list)

    ask = client.post(
        "/projects/project-a/ask",
        json={"question": "Como funciona refresh token?", "top_k": 3},
    )
    assert ask.status_code == 200
    assert ask.json()["status"] == "ok"
    assert ask.json()["data"]["answer_short"]

    stats = client.get("/projects/project-a/stats")
    assert stats.status_code == 200
    assert stats.json()["status"] == "ok"
    assert "stats" in stats.json()["data"]

