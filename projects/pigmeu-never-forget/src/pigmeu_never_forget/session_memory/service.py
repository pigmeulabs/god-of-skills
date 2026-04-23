"""Session memory storage backed by markdown files."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pigmeu_never_forget.app import create_application
from pigmeu_never_forget.config.loader import load_workspace_settings
from pigmeu_never_forget.domain.enums import ErrorCode
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.utils.paths import slugify


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _utcnow()).isoformat(timespec="seconds")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _find_git_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _state_session_file(state: dict[str, Any]) -> Path:
    return Path(str(state["session_file"]))


def _split_front_matter(content: str) -> tuple[dict[str, Any], str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "<!-- pnf-session-state":
        return {}, content
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "-->":
            front_matter = "\n".join(lines[1:index]).strip()
            body = "\n".join(lines[index + 1 :])
            if not front_matter:
                return {}, body
            try:
                payload = json.loads(front_matter)
            except json.JSONDecodeError:
                return {}, body
            return payload if isinstance(payload, dict) else {}, body
    return {}, content


def _format_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    if not rows:
        return "_Sem registros._"
    header = "| " + " | ".join(label for _, label in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body_rows: list[str] = []
    for row in rows:
        values = []
        for key, _ in columns:
            value = row.get(key, "")
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=True, sort_keys=True)
            values.append(str(value).replace("\n", " "))
        body_rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, separator, *body_rows])


def _dedupe_changed_files(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for item in items:
        path = str(item.get("path") or item.get("file_path") or "").strip()
        if not path:
            continue
        latest[path] = {
            "name": str(item.get("name") or Path(path).name),
            "path": path,
            "change_type": str(item.get("change_type") or item.get("status") or "modified"),
            "timestamp": str(item.get("timestamp") or _iso()),
        }
    return sorted(latest.values(), key=lambda entry: entry["path"])


def _merge_token_totals(current: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    result = dict(current)
    for key in ("input", "response", "other_tools"):
        value = incoming.get(key)
        if value is None:
            result.setdefault(key, None)
            continue
        previous = result.get(key)
        if previous is None:
            result[key] = int(value)
        else:
            result[key] = int(previous) + int(value)
    return result


def _merge_usage_ledger(
    current: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
    key_fields: tuple[str, str] = ("name", "type"),
) -> list[dict[str, Any]]:
    ledger = {tuple(item.get(field, "") for field in key_fields): dict(item) for item in current}
    for item in incoming:
        key = tuple(str(item.get(field, "")).strip() for field in key_fields)
        if not any(key):
            continue
        existing = ledger.get(key, {
            "name": str(item.get("name") or ""),
            "type": str(item.get("type") or "tool"),
            "uses": 0,
            "input_tokens": None,
            "response_tokens": None,
            "other_tools_tokens": None,
            "interactions": 0,
        })
        existing["uses"] = int(existing.get("uses") or 0) + int(item.get("uses") or 1)
        existing["interactions"] = int(existing.get("interactions") or 0) + int(item.get("interactions") or 1)
        for field in ("input_tokens", "response_tokens", "other_tools_tokens"):
            value = item.get(field)
            if value is None:
                existing.setdefault(field, None)
                continue
            previous = existing.get(field)
            existing[field] = int(value) if previous is None else int(previous) + int(value)
        ledger[key] = existing
    return list(ledger.values())


def _merge_usage_entities(
    current: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
    *,
    name_field: str = "name",
) -> list[dict[str, Any]]:
    entities = {str(item.get(name_field, "")).strip(): dict(item) for item in current}
    for item in incoming:
        name = str(item.get(name_field, "")).strip()
        if not name:
            continue
        existing = entities.get(
            name,
            {
                name_field: name,
                "interactions": 0,
                "input_tokens": None,
                "response_tokens": None,
                "other_tools_tokens": None,
            },
        )
        existing["interactions"] = int(existing.get("interactions") or 0) + int(item.get("interactions") or 1)
        for field in ("input_tokens", "response_tokens", "other_tools_tokens"):
            value = item.get(field)
            if value is None:
                existing.setdefault(field, None)
                continue
            previous = existing.get(field)
            existing[field] = int(value) if previous is None else int(previous) + int(value)
        for extra_field in ("role", "kind", "id"):
            if item.get(extra_field) is not None:
                existing.setdefault(extra_field, item.get(extra_field))
        entities[name] = existing
    return list(entities.values())


@dataclass(slots=True)
class SessionMemoryService:
    """Persist session transcripts and operational metadata."""

    repo_root: Path | None = None
    session_root: Path | None = None
    config_path: str | None = None
    archive_project_id: str | None = None
    archive_client: Any | None = None
    inactivity_timeout_hours: int = 8
    _session_root: Path = field(init=False, repr=False)

    def __post_init__(self) -> None:
        repo_root = self.repo_root or Path(__file__).resolve().parents[3]
        self.repo_root = repo_root.resolve()
        self._session_root = (self.session_root or (self.repo_root / "docs" / "memories" / "sessions")).resolve()
        self._session_root.mkdir(parents=True, exist_ok=True)
        if self.config_path:
            try:
                settings = load_workspace_settings(self.config_path)
                session_settings = settings.get("session_memory", {}) if isinstance(settings, dict) else {}
                if self.inactivity_timeout_hours == 8 and session_settings.get("inactivity_timeout_hours") is not None:
                    self.inactivity_timeout_hours = int(session_settings.get("inactivity_timeout_hours"))
                archive_project_id = str(session_settings.get("archive_project_id") or "").strip()
                if not self.archive_project_id and archive_project_id:
                    self.archive_project_id = archive_project_id
            except Exception:
                pass
        if self.archive_project_id is None:
            self.archive_project_id = slugify(self.repo_root.name)

    def start_session(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = dict(payload or {})
        started_at = str(payload.get("started_at") or _iso())
        session_id = str(payload.get("session_id") or uuid.uuid4().hex[:8])
        stem = str(payload.get("session_stem") or self._build_stem(started_at, session_id))
        session_dir = self._session_root / stem
        session_file = session_dir / f"{stem}.md"
        if session_file.exists():
            raise AppError(
                code=ErrorCode.INVALID_REQUEST,
                message=f"Session already exists: {stem}",
                details={"session_stem": stem, "session_file": str(session_file)},
            )
        state = self._initial_state(payload, stem=stem, session_id=session_id, started_at=started_at)
        _atomic_write(session_file, self._render_markdown(state))
        return self.get_session_status({"session_stem": stem})

    def append_turn(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._load_state(payload)
        turn_timestamp = str(payload.get("timestamp") or _iso())
        turn = self._build_turn(payload, timestamp=turn_timestamp)
        state["turns"].append(turn)
        state["turn_count"] = len(state["turns"])
        state["interaction_count"] = int(state.get("interaction_count") or 0) + 1
        state["updated_at"] = turn_timestamp
        state["last_activity_at"] = turn_timestamp
        state["summary"] = self._update_summary(state.get("summary", {}), payload, turn)
        self._apply_metrics(state, payload.get("metrics") or payload)
        state["changed_files"] = _dedupe_changed_files(
            [*state.get("changed_files", []), *self._coerce_changed_files(payload, turn_timestamp)]
        )
        state["tools"] = _merge_usage_ledger(state.get("tools", []), self._coerce_usage_entries(payload, "tools", "tool"))
        state["agents"] = _merge_usage_entities(state.get("agents", []), self._coerce_usage_entries(payload, "agents", "agent"))
        state["humans"] = _merge_usage_entities(state.get("humans", []), self._coerce_usage_entries(payload, "humans", "human"))
        if model := str(payload.get("model") or turn.get("model") or "").strip():
            models = state.setdefault("models", {})
            model_entry = dict(models.get(model) or {"interactions": 0, "input_tokens": None, "response_tokens": None, "other_tools_tokens": None})
            model_entry["interactions"] = int(model_entry.get("interactions") or 0) + 1
            metrics = payload.get("metrics") or {}
            for field, target in (
                ("input_tokens", "input_tokens"),
                ("response_tokens", "response_tokens"),
                ("other_tools_tokens", "other_tools_tokens"),
            ):
                value = metrics.get(field)
                if value is None:
                    model_entry.setdefault(target, None)
                    continue
                previous = model_entry.get(target)
                model_entry[target] = int(value) if previous is None else int(previous) + int(value)
            models[model] = model_entry
        _atomic_write(_state_session_file(state), self._render_markdown(state))
        return self.get_session_status({"session_stem": state["session_stem"]})

    def update_metrics(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._load_state(payload)
        self._apply_metrics(state, payload)
        if isinstance(payload.get("models"), dict):
            for model_name, model_metrics in payload["models"].items():
                model_entry = dict(state.get("models", {}).get(model_name) or {})
                model_entry.setdefault("interactions", 0)
                model_entry["interactions"] = int(model_entry.get("interactions") or 0) + int(
                    model_metrics.get("interactions") or 0
                )
                for field in ("input_tokens", "response_tokens", "other_tools_tokens"):
                    value = model_metrics.get(field)
                    if value is None:
                        model_entry.setdefault(field, None)
                        continue
                    previous = model_entry.get(field)
                    model_entry[field] = int(value) if previous is None else int(previous) + int(value)
                state.setdefault("models", {})[model_name] = model_entry
        _atomic_write(_state_session_file(state), self._render_markdown(state))
        return self.get_session_status({"session_stem": state["session_stem"]})

    def record_response(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Record one assistant response, ensuring active-session lifecycle automatically."""
        payload = dict(payload or {})
        archive = bool(payload.get("archive_stale", True))
        latest = self.find_latest_session()
        stale_finalized: dict[str, Any] | None = None
        session_stem = str(payload.get("session_stem") or "").strip()

        if session_stem:
            state = self._load_state({"session_stem": session_stem})
            status = str(state.get("status") or "")
            is_stale = self.is_stale(session_stem) if status == "active" else False
            if status != "active" or is_stale:
                if status == "active" and is_stale and archive:
                    stale_finalized = self.finalize_session({"session_stem": session_stem, "archive": True})
                started = self.start_session(
                    {
                        "project_name": payload.get("project_name") or state.get("project_name"),
                        "project_id": payload.get("project_id") or state.get("project_id"),
                        "summary_short": payload.get("summary_short") or "",
                        "summary_full": payload.get("summary_full") or "",
                    }
                )
                session_stem = str(started.get("session_stem"))
        else:
            if isinstance(latest, dict) and latest.get("session_stem") and latest.get("status") == "active":
                candidate = str(latest.get("session_stem"))
                if latest.get("is_stale"):
                    if archive:
                        stale_finalized = self.finalize_session({"session_stem": candidate, "archive": True})
                    started = self.start_session(
                        {
                            "project_name": payload.get("project_name") or latest.get("project_name"),
                            "project_id": payload.get("project_id") or latest.get("project_id"),
                            "summary_short": payload.get("summary_short") or "",
                            "summary_full": payload.get("summary_full") or "",
                        }
                    )
                    session_stem = str(started.get("session_stem"))
                else:
                    session_stem = candidate
            else:
                started = self.start_session(
                    {
                        "project_name": payload.get("project_name") or self.repo_root.name,
                        "project_id": payload.get("project_id") or slugify(self.repo_root.name),
                        "summary_short": payload.get("summary_short") or "",
                        "summary_full": payload.get("summary_full") or "",
                    }
                )
                session_stem = str(started.get("session_stem"))

        append_payload = dict(payload)
        append_payload["session_stem"] = session_stem
        appended = self.append_turn(append_payload)
        result = {
            "session": appended,
            "stale_finalized": stale_finalized,
            "latest_before_record": latest,
        }
        if bool(payload.get("finalize", False)):
            result["finalized"] = self.finalize_session({"session_stem": session_stem, "archive": True})
        return result

    def rollover_stale_sessions(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Finalize and archive every stale active session under docs/memories/sessions."""
        payload = dict(payload or {})
        archive = bool(payload.get("archive", True))
        processed: list[dict[str, Any]] = []
        for session_file in sorted(self._session_root.glob("*/*.md")):
            try:
                state = self._read_state(session_file)
            except Exception:  # noqa: BLE001
                continue
            if state.get("status") != "active":
                continue
            session_stem = str(state.get("session_stem") or "")
            if not session_stem:
                continue
            if not self.is_stale(session_stem):
                continue
            if archive:
                finalized = self.finalize_session({"session_stem": session_stem, "archive": True})
                processed.append(finalized)
            else:
                state["status"] = "finalized"
                state["closed_at"] = state.get("closed_at") or _iso()
                state["updated_at"] = _iso()
                _atomic_write(session_file, self._render_markdown(state))
                processed.append(self._status_payload(state))
        return {"processed": processed, "count": len(processed)}

    def finalize_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._load_state(payload)
        finalized_at = str(payload.get("finalized_at") or _iso())
        state["status"] = "finalized"
        state["closed_at"] = finalized_at
        state["updated_at"] = finalized_at
        archive = bool(payload.get("archive", True))
        archive_result: dict[str, Any] | None = None
        if archive:
            archive_result = self._archive_session(state, payload)
            state["archive"] = archive_result
            state["status"] = "archived" if archive_result.get("status") == "ok" else "finalized"
        _atomic_write(_state_session_file(state), self._render_markdown(state))
        result = self.get_session_status({"session_stem": state["session_stem"]})
        result["archive_result"] = archive_result
        return result

    def archive_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._load_state(payload)
        archive_result = self._archive_session(state, payload)
        state["archive"] = archive_result
        if archive_result.get("status") == "ok" and state.get("status") != "finalized":
            state["status"] = "archived"
            state["closed_at"] = state.get("closed_at") or _iso()
            state["updated_at"] = _iso()
        _atomic_write(_state_session_file(state), self._render_markdown(state))
        return self.get_session_status({"session_stem": state["session_stem"]})

    def get_session_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_stem = str(payload.get("session_stem") or "").strip()
        session_file = self._session_root / session_stem / f"{session_stem}.md"
        if not session_file.exists():
            raise AppError(
                code=ErrorCode.SESSION_NOT_FOUND,
                message=f"Session not found: {session_stem}",
                details={"session_stem": session_stem, "session_file": str(session_file)},
            )
        state = self._read_state(session_file)
        return self._status_payload(state)

    def find_latest_session(self) -> dict[str, Any] | None:
        candidates: list[dict[str, Any]] = []
        for session_file in self._session_root.glob("*/*.md"):
            try:
                state = self._read_state(session_file)
            except Exception:  # noqa: BLE001
                continue
            candidates.append(self._status_payload(state))
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.get("updated_at") or "")

    def is_stale(self, session_stem: str) -> bool:
        state = self._read_state(self._session_root / session_stem / f"{session_stem}.md")
        last_activity = _parse_iso(str(state.get("last_activity_at") or state.get("updated_at") or ""))
        if last_activity is None:
            return False
        return _utcnow() - last_activity > timedelta(hours=self.inactivity_timeout_hours)

    def _initial_state(self, payload: dict[str, Any], *, stem: str, session_id: str, started_at: str) -> dict[str, Any]:
        summary = {
            "short": str(payload.get("summary_short") or ""),
            "full": str(payload.get("summary_full") or ""),
        }
        return {
            "session_id": session_id,
            "session_stem": stem,
            "project_name": str(payload.get("project_name") or self.repo_root.name),
            "project_id": str(payload.get("project_id") or slugify(str(payload.get("project_name") or self.repo_root.name))),
            "started_at": started_at,
            "updated_at": started_at,
            "last_activity_at": started_at,
            "closed_at": None,
            "status": "active",
            "summary": summary,
            "turn_count": 0,
            "interaction_count": 0,
            "token_totals": {"input": None, "response": None, "other_tools": None},
            "memory_tokens_used": payload.get("memory_tokens_used"),
            "models": {},
            "changed_files": _dedupe_changed_files(self._coerce_changed_files(payload, started_at)),
            "tools": _merge_usage_ledger([], self._coerce_usage_entries(payload, "tools", "tool")),
            "agents": _merge_usage_entities([], self._coerce_usage_entries(payload, "agents", "agent")),
            "humans": _merge_usage_entities([], self._coerce_usage_entries(payload, "humans", "human")),
            "turns": [],
            "archive": {
                "status": "pending",
                "archive_project_id": self.archive_project_id,
                "archived_at": None,
                "archive_result": None,
            },
            "session_root": str(self._session_root),
            "session_file": str(self._session_root / stem / f"{stem}.md"),
        }

    def _build_stem(self, started_at: str, session_id: str) -> str:
        dt = _parse_iso(started_at) or _utcnow()
        return f"{dt.strftime('%y-%m-%d-%H-%M')}-session-{session_id}"

    def _load_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_stem = str(payload.get("session_stem") or payload.get("session_id") or "").strip()
        if not session_stem:
            raise AppError(
                code=ErrorCode.INVALID_REQUEST,
                message="session_stem is required",
                details={"payload_keys": sorted(payload.keys())},
            )
        session_file = self._session_root / session_stem / f"{session_stem}.md"
        if not session_file.exists():
            raise AppError(
                code=ErrorCode.SESSION_NOT_FOUND,
                message=f"Session not found: {session_stem}",
                details={"session_stem": session_stem, "session_file": str(session_file)},
            )
        return self._read_state(session_file)

    def _read_state(self, session_file: Path) -> dict[str, Any]:
        content = session_file.read_text(encoding="utf-8")
        data, body = _split_front_matter(content)
        data.setdefault("session_file", str(session_file))
        data.setdefault("session_root", str(session_file.parent.parent))
        data["body"] = body
        if not isinstance(data.get("turns"), list):
            data["turns"] = []
        if not isinstance(data.get("tools"), list):
            data["tools"] = []
        if not isinstance(data.get("agents"), list):
            data["agents"] = []
        if not isinstance(data.get("humans"), list):
            data["humans"] = []
        if not isinstance(data.get("changed_files"), list):
            data["changed_files"] = []
        if not isinstance(data.get("models"), dict):
            data["models"] = {}
        data.setdefault("summary", {"short": "", "full": ""})
        data.setdefault("token_totals", {"input": None, "response": None, "other_tools": None})
        if not isinstance(data.get("archive"), dict):
            data["archive"] = {"status": "pending", "archive_project_id": self.archive_project_id, "archived_at": None}
        return data

    def _render_markdown(self, state: dict[str, Any]) -> str:
        front_matter = {
            key: value
            for key, value in state.items()
            if key not in {"body", "session_root", "session_file"}
        }
        body = self._render_body(front_matter)
        state_block = json.dumps(front_matter, ensure_ascii=True, indent=2, sort_keys=False)
        return "<!-- pnf-session-state\n" + state_block + "\n-->\n\n" + body.strip() + "\n"

    def _render_body(self, state: dict[str, Any]) -> str:
        summary = state.get("summary") or {}
        archive = state.get("archive") or {}
        body_parts = [
            f"# Session {state.get('session_stem')}",
            "",
            "## Overview",
            f"- Project: `{state.get('project_name')}`",
            f"- Project ID: `{state.get('project_id')}`",
            f"- Session ID: `{state.get('session_id')}`",
            f"- Status: `{state.get('status')}`",
            f"- Started: `{state.get('started_at')}`",
            f"- Updated: `{state.get('updated_at')}`",
            f"- Closed: `{state.get('closed_at') or 'n/a'}`",
            f"- Turns: `{state.get('turn_count', 0)}`",
            f"- Interactions: `{state.get('interaction_count', 0)}`",
            "",
            "## Summary",
            summary.get("short") or "_Sem resumo curto._",
            "",
            summary.get("full") or "_Sem resumo longo._",
            "",
            "## Token Metrics",
            f"- Input tokens: `{(state.get('token_totals') or {}).get('input')}`",
            f"- Response tokens: `{(state.get('token_totals') or {}).get('response')}`",
            f"- Other tools tokens: `{(state.get('token_totals') or {}).get('other_tools')}`",
            f"- Memory tokens used: `{state.get('memory_tokens_used')}`",
            "",
            "## Models",
            _format_table(
                [
                    {
                        "name": name,
                        "interactions": values.get("interactions", 0),
                        "input_tokens": values.get("input_tokens"),
                        "response_tokens": values.get("response_tokens"),
                        "other_tools_tokens": values.get("other_tools_tokens"),
                    }
                    for name, values in sorted((state.get("models") or {}).items())
                ],
                [
                    ("name", "Model"),
                    ("interactions", "Interactions"),
                    ("input_tokens", "Input"),
                    ("response_tokens", "Response"),
                    ("other_tools_tokens", "Other"),
                ],
            ),
            "",
            "## Changed Files",
            _format_table(
                state.get("changed_files") or [],
                [("name", "Name"), ("path", "Path"), ("change_type", "Type"), ("timestamp", "Timestamp")],
            ),
            "",
            "## Tools / Skills / MCPs",
            _format_table(
                state.get("tools") or [],
                [
                    ("name", "Name"),
                    ("type", "Type"),
                    ("uses", "Uses"),
                    ("input_tokens", "Input"),
                    ("response_tokens", "Response"),
                    ("other_tools_tokens", "Other"),
                    ("interactions", "Interactions"),
                ],
            ),
            "",
            "## Agents",
            _format_table(
                state.get("agents") or [],
                [
                    ("name", "Name"),
                    ("interactions", "Interactions"),
                    ("input_tokens", "Input"),
                    ("response_tokens", "Response"),
                    ("other_tools_tokens", "Other"),
                ],
            ),
            "",
            "## Humans",
            _format_table(
                state.get("humans") or [],
                [("name", "Name"), ("interactions", "Interactions")],
            ),
            "",
            "## Timeline",
        ]
        turns = state.get("turns") or []
        if not turns:
            body_parts.append("_Sem interações registradas._")
        else:
            for index, turn in enumerate(turns, start=1):
                body_parts.extend(
                    [
                        f"### Turn {index}",
                        f"- Timestamp: `{turn.get('timestamp')}`",
                        f"- Role: `{turn.get('role')}`",
                        f"- Model: `{turn.get('model')}`",
                        f"- Agent: `{turn.get('agent')}`",
                        "",
                        "#### Prompt",
                        turn.get("prompt") or "_Sem prompt._",
                        "",
                        "#### Response",
                        turn.get("response") or "_Sem resposta._",
                        "",
                        "#### Notes",
                        f"- Summary: {turn.get('summary_short') or '_n/a_'}",
                        f"- Input tokens: `{turn.get('input_tokens')}`",
                        f"- Response tokens: `{turn.get('response_tokens')}`",
                        f"- Other tools tokens: `{turn.get('other_tools_tokens')}`",
                        "",
                    ]
                )
        body_parts.extend(
            [
                "## Archive",
                f"- Status: `{archive.get('status')}`",
                f"- Archive project: `{archive.get('archive_project_id')}`",
                f"- Archived at: `{archive.get('archived_at') or 'n/a'}`",
                f"- Archive result: `{archive.get('archive_result')}`",
            ]
        )
        return "\n".join(body_parts)

    def _status_payload(self, state: dict[str, Any]) -> dict[str, Any]:
        updated_at = _parse_iso(str(state.get("updated_at") or state.get("last_activity_at") or ""))
        age_seconds = int((_utcnow() - updated_at).total_seconds()) if updated_at else None
        return {
            "session_id": state.get("session_id"),
            "session_stem": state.get("session_stem"),
            "session_file": state.get("session_file"),
            "project_name": state.get("project_name"),
            "project_id": state.get("project_id"),
            "status": state.get("status"),
            "started_at": state.get("started_at"),
            "updated_at": state.get("updated_at"),
            "last_activity_at": state.get("last_activity_at"),
            "closed_at": state.get("closed_at"),
            "age_seconds": age_seconds,
            "is_stale": bool(age_seconds is not None and age_seconds > self.inactivity_timeout_hours * 3600),
            "summary": state.get("summary"),
            "turn_count": state.get("turn_count", 0),
            "interaction_count": state.get("interaction_count", 0),
            "token_totals": state.get("token_totals"),
            "memory_tokens_used": state.get("memory_tokens_used"),
            "models": state.get("models", {}),
            "changed_files": state.get("changed_files", []),
            "tools": state.get("tools", []),
            "agents": state.get("agents", []),
            "humans": state.get("humans", []),
            "archive": state.get("archive", {}),
        }

    def _update_summary(self, current: dict[str, Any], payload: dict[str, Any], turn: dict[str, Any]) -> dict[str, Any]:
        summary = dict(current or {})
        if payload.get("summary_short") is not None:
            summary["short"] = str(payload.get("summary_short") or "")
        elif not summary.get("short") and turn.get("response"):
            summary["short"] = str(turn.get("response"))[:240]
        if payload.get("summary_full") is not None:
            summary["full"] = str(payload.get("summary_full") or "")
        elif not summary.get("full") and turn.get("response"):
            summary["full"] = str(turn.get("response"))[:1200]
        return summary

    def _apply_metrics(self, state: dict[str, Any], metrics: dict[str, Any]) -> None:
        token_totals = state.setdefault("token_totals", {"input": None, "response": None, "other_tools": None})
        for key in ("input", "response", "other_tools"):
            value = metrics.get(f"{key}_tokens")
            if value is None and key == "input":
                value = metrics.get("input_tokens")
            if value is None and key == "response":
                value = metrics.get("response_tokens")
            if value is None and key == "other_tools":
                value = metrics.get("other_tools_tokens")
            if value is None:
                continue
            previous = token_totals.get(key)
            token_totals[key] = int(value) if previous is None else int(previous) + int(value)
        if metrics.get("memory_tokens_used") is not None:
            previous = state.get("memory_tokens_used")
            value = metrics.get("memory_tokens_used")
            state["memory_tokens_used"] = int(value) if previous is None else int(previous) + int(value)

    def _coerce_changed_files(self, payload: dict[str, Any], timestamp: str) -> list[dict[str, Any]]:
        changed_files = payload.get("changed_files")
        if isinstance(changed_files, list) and changed_files:
            items = []
            for item in changed_files:
                if isinstance(item, dict):
                    items.append({**item, "timestamp": item.get("timestamp") or timestamp})
            return items
        git_root = _find_git_root(self.repo_root)
        if git_root is None:
            return []
        try:
            result = subprocess.run(
                ["git", "-C", str(git_root), "status", "--porcelain=v1"],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:  # noqa: BLE001
            return []
        items: list[dict[str, Any]] = []
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            status = line[:2].strip() or "modified"
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
                status = "renamed"
            items.append(
                {
                    "name": Path(path).name,
                    "path": path,
                    "change_type": status,
                    "timestamp": timestamp,
                }
            )
        return items

    def _coerce_usage_entries(
        self,
        payload: dict[str, Any],
        plural_key: str,
        default_type: str,
    ) -> list[dict[str, Any]]:
        entries = payload.get(plural_key) or payload.get(f"{plural_key}_used") or []
        if not isinstance(entries, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in entries:
            if isinstance(item, str):
                normalized.append({"name": item, "type": default_type, "uses": 1, "interactions": 1})
                continue
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "name": str(item.get("name") or item.get("id") or ""),
                    "type": str(item.get("type") or default_type),
                    "uses": int(item.get("uses") or item.get("count") or 1),
                    "interactions": int(item.get("interactions") or 1),
                    "input_tokens": item.get("input_tokens"),
                    "response_tokens": item.get("response_tokens"),
                    "other_tools_tokens": item.get("other_tools_tokens"),
                    "role": item.get("role"),
                    "kind": item.get("kind"),
                    "id": item.get("id"),
                }
            )
        return normalized

    def _build_turn(self, payload: dict[str, Any], *, timestamp: str) -> dict[str, Any]:
        prompt = str(payload.get("prompt") or payload.get("user_message") or payload.get("input") or "")
        response = str(payload.get("response") or payload.get("assistant_message") or payload.get("output") or "")
        metrics = payload.get("metrics") or {}
        return {
            "turn_id": str(payload.get("turn_id") or uuid.uuid4().hex[:12]),
            "timestamp": timestamp,
            "role": str(payload.get("role") or "assistant"),
            "model": str(payload.get("model") or ""),
            "agent": str(payload.get("agent") or payload.get("agent_name") or "codex"),
            "prompt": prompt,
            "response": response,
            "summary_short": str(payload.get("summary_short") or ""),
            "summary_full": str(payload.get("summary_full") or ""),
            "input_tokens": metrics.get("input_tokens", payload.get("input_tokens")),
            "response_tokens": metrics.get("response_tokens", payload.get("response_tokens")),
            "other_tools_tokens": metrics.get("other_tools_tokens", payload.get("other_tools_tokens")),
            "memory_tokens_used": metrics.get("memory_tokens_used", payload.get("memory_tokens_used")),
            "tools": self._coerce_usage_entries(payload, "tools", "tool"),
            "changed_files": self._coerce_changed_files(payload, timestamp),
            "humans": self._coerce_usage_entries(payload, "humans", "human"),
            "agents": self._coerce_usage_entries(payload, "agents", "agent"),
        }

    def _archive_session(self, state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        archive_project_id = str(payload.get("archive_project_id") or self.archive_project_id or slugify(self.repo_root.name))
        archive_client = self.archive_client
        if archive_client is None:
            archive_client = create_application(self.config_path)
            archive_client.initialize_workspace()
            self.archive_client = archive_client
        title = f"session:{state['session_stem']}"
        session_text = self._render_markdown(state).strip()
        try:
            result = archive_client.index_text(
                project_id=archive_project_id,
                title=title,
                text=session_text,
                source_type="session_memory",
                tags=["session", "memory", state.get("project_id") or "workspace"],
            )
            return {
                "status": "ok",
                "archive_project_id": archive_project_id,
                "archived_at": _iso(),
                "archive_result": result,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "archive_project_id": archive_project_id,
                "archived_at": None,
                "archive_result": {"error": str(exc)},
            }
