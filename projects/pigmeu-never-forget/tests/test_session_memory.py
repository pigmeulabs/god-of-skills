from __future__ import annotations

from pathlib import Path

from pigmeu_never_forget.session_memory.adapter import SessionMemoryAdapter
from pigmeu_never_forget.session_memory.service import SessionMemoryService


class StubArchiveClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def index_text(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(kwargs)
        return {"status": "ok", "data": kwargs}


def test_session_service_writes_incremental_markdown(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    service = SessionMemoryService(repo_root=repo_root, archive_client=StubArchiveClient(), archive_project_id="archive-proj")

    started = service.start_session({"project_name": "demo", "project_id": "demo", "summary_short": "Init"})
    stem = started["session_stem"]

    appended = service.append_turn(
        {
            "session_stem": stem,
            "prompt": "Como funciona?",
            "response": "Funciona assim.",
            "model": "gpt-test",
            "metrics": {"input_tokens": 3, "response_tokens": 7},
            "tools": [{"name": "pnf-mcp", "type": "MCP", "uses": 2}],
            "changed_files": [{"path": "src/app.py", "change_type": "modified"}],
            "humans": ["alice"],
            "agents": ["codex"],
        }
    )

    assert appended["turn_count"] == 1
    assert appended["status"] == "active"
    assert appended["token_totals"]["input"] == 3
    assert appended["models"]["gpt-test"]["interactions"] == 1
    assert appended["changed_files"][0]["path"] == "src/app.py"

    finalized = service.finalize_session({"session_stem": stem})
    assert finalized["status"] == "archived"
    assert finalized["archive"]["status"] == "ok"

    session_file = repo_root / "docs" / "memories" / "sessions" / stem / f"{stem}.md"
    content = session_file.read_text(encoding="utf-8")
    assert f"Session {stem}" in content
    assert "src/app.py" in content
    assert "pnf-mcp" in content
    assert "Funciona assim." in content


def test_record_response_rolls_over_stale_session(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    service = SessionMemoryService(repo_root=repo_root, archive_client=StubArchiveClient(), archive_project_id="archive-proj")

    stale = service.start_session(
        {
            "project_name": "demo",
            "project_id": "demo",
            "started_at": "2020-01-01T00:00:00+00:00",
        }
    )

    recorded = service.record_response(
        {
            "prompt": "Novo passo?",
            "response": "Sessao nova criada automaticamente.",
            "model": "gpt-test",
            "metrics": {"input_tokens": 2, "response_tokens": 5},
        }
    )

    assert recorded["stale_finalized"] is not None
    assert recorded["stale_finalized"]["status"] == "archived"
    assert recorded["stale_finalized"]["session_stem"] == stale["session_stem"]
    assert recorded["session"]["status"] == "active"
    assert recorded["session"]["turn_count"] == 1
    assert recorded["session"]["session_stem"] != stale["session_stem"]


def test_session_adapter_returns_mcp_envelopes(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    adapter = SessionMemoryAdapter(repo_root=str(repo_root), archive_project_id="archive-proj")
    adapter.service.archive_client = StubArchiveClient()

    created = adapter.start_session({"project_name": "demo", "project_id": "demo"})
    assert created["status"] == "ok"
    stem = created["data"]["session_stem"]

    status = adapter.get_session_status({"session_stem": stem})
    assert status["status"] == "ok"
    assert status["data"]["session_stem"] == stem

    recorded = adapter.record_response(
        {
            "session_stem": stem,
            "prompt": "Qual o status?",
            "response": "Sessao atualizada.",
            "model": "gpt-test",
        }
    )
    assert recorded["status"] == "ok"
    assert recorded["data"]["session"]["turn_count"] == 1

    stale_started = SessionMemoryService(repo_root=repo_root).start_session(
        {
            "project_name": "stale-demo",
            "project_id": "stale-demo",
            "started_at": "2020-01-01T00:00:00+00:00",
        }
    )
    assert SessionMemoryService(repo_root=repo_root).is_stale(stale_started["session_stem"]) is True
