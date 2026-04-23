#!/usr/bin/env python3
"""Shared helpers for pnf-session-memory-ops scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PNF_REPO = "/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget"
DEFAULT_CONFIG_PATH = "/home/ubuntu/projects-workspace/.opencode/pnf-workspace-config.yaml"
DEFAULT_ARCHIVE_PROJECT_ID = "pigmeu-never-forget"


def repo_path() -> Path:
    return Path(os.environ.get("PNF_REPO_PATH", DEFAULT_PNF_REPO)).resolve()


def config_path() -> Path:
    return Path(os.environ.get("PNF_CONFIG_PATH", DEFAULT_CONFIG_PATH)).resolve()


def archive_project_id() -> str:
    return os.environ.get("PNF_SESSION_ARCHIVE_PROJECT_ID", DEFAULT_ARCHIVE_PROJECT_ID)


def prefer_mcp() -> bool:
    return os.environ.get("PNF_SESSION_PREFER_MCP", "1").strip() not in {"0", "false", "False"}


def run_session_cli(args: list[str]) -> tuple[str, dict[str, Any]]:
    repo = repo_path()
    cmd = [
        "python3",
        "-m",
        "pigmeu_never_forget.session_memory.cli",
        "--config",
        str(config_path()),
        "--repo-root",
        str(repo),
        "--archive-project-id",
        archive_project_id(),
        *args,
    ]
    env = dict(os.environ)
    src = repo / "src"
    env["PYTHONPATH"] = str(src) if not env.get("PYTHONPATH") else f"{src}:{env['PYTHONPATH']}"
    completed = subprocess.run(cmd, cwd=repo, check=False, capture_output=True, text=True, env=env)
    command = (
        f"PYTHONPATH={src} python3 -m pigmeu_never_forget.session_memory.cli "
        f"--config {config_path()} --repo-root {repo} --archive-project-id {archive_project_id()} {' '.join(args)}"
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"Command failed ({completed.returncode}): {stderr}")
    stdout = completed.stdout.strip()
    return command, json.loads(stdout) if stdout else {}


def run_session_mcp_tool(tool: str, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    repo = repo_path()
    cmd = [
        "python3",
        "-m",
        "pigmeu_never_forget.session_memory.local_call",
        tool,
        "--config",
        str(config_path()),
        "--repo-root",
        str(repo),
        "--archive-project-id",
        archive_project_id(),
        "--payload",
        json.dumps(payload, ensure_ascii=True),
    ]
    env = dict(os.environ)
    src = repo / "src"
    env["PYTHONPATH"] = str(src) if not env.get("PYTHONPATH") else f"{src}:{env['PYTHONPATH']}"
    completed = subprocess.run(cmd, cwd=repo, check=False, capture_output=True, text=True, env=env)
    command = (
        f"PYTHONPATH={src} python3 -m pigmeu_never_forget.session_memory.local_call "
        f"{tool} --config {config_path()} --repo-root {repo} --archive-project-id {archive_project_id()} "
        f"--payload '{json.dumps(payload, ensure_ascii=True)}'"
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"MCP call failed ({completed.returncode}): {stderr}")
    stdout = completed.stdout.strip()
    return command, json.loads(stdout) if stdout else {}


def run_with_mcp_fallback(tool: str, payload: dict[str, Any], cli_args: list[str]) -> tuple[str, dict[str, Any], str]:
    if prefer_mcp():
        try:
            command, result = run_session_mcp_tool(tool, payload)
            return command, result, "mcp"
        except Exception:
            pass
    command, result = run_session_cli(cli_args)
    return command, result, "cli"


def print_envelope(command: str, summary: str, next_step: str, data: dict[str, Any]) -> None:
    payload = {
        "command_executed": command,
        "summary": summary,
        "next_step": next_step,
        "data": data,
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))


def fail(message: str) -> None:
    payload = {
        "command_executed": None,
        "summary": "Falha na automacao.",
        "next_step": "Revise o erro e execute novamente.",
        "error": {
            "code": "INTERNAL_ERROR",
            "message": message,
            "retryable": False,
            "details": {},
        },
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    sys.exit(1)


def read_payload(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    payload = json.loads(raw)
    return payload if isinstance(payload, dict) else {}


def temp_payload_file(payload: dict[str, Any]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
    with handle:
        json.dump(payload, handle, ensure_ascii=True)
    return Path(handle.name)
