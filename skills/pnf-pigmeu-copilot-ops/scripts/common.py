#!/usr/bin/env python3
"""Shared helpers for pnf-pigmeu-copilot-ops scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PNF_REPO = "/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget"
DEFAULT_PROJECT_PATH = "/home/ubuntu/projects-workspace/pigmeu-copilot"
DEFAULT_PROJECT_ID = "pigmeu-copilot"


def pnf_repo_path() -> Path:
    return Path(os.environ.get("PNF_REPO_PATH", DEFAULT_PNF_REPO)).resolve()


def project_path() -> Path:
    return Path(os.environ.get("PNF_PROJECT_PATH", DEFAULT_PROJECT_PATH)).resolve()


def project_id() -> str:
    return os.environ.get("PNF_PROJECT_ID", DEFAULT_PROJECT_ID)


def workspace_root() -> Path:
    return Path(os.environ.get("PNF_WORKSPACE_ROOT", str(project_path().parent))).resolve()


def config_path() -> Path:
    if os.environ.get("PNF_CONFIG_PATH"):
        return Path(os.environ["PNF_CONFIG_PATH"]).resolve()
    root = workspace_root()
    content = (
        "workspace:\n"
        f"  root_path: {root}\n"
        "  project_dir_mode: immediate_children\n"
        "  ignore_dirs:\n"
        "    - _workspace\n"
        "    - .git\n"
        "storage:\n"
        "  collection_prefix: kb_\n"
    )
    path = Path(tempfile.gettempdir()) / "pnf-pigmeu-copilot-ops-config.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def run_pnf_cli(args: list[str]) -> tuple[str, dict[str, Any]]:
    repo = pnf_repo_path()
    config = config_path()
    cmd = [
        "python3",
        "-m",
        "pigmeu_never_forget.cli",
        "--config",
        str(config),
        *args,
    ]
    env = dict(os.environ)
    src = repo / "src"
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src) if not existing_path else f"{src}:{existing_path}"
    completed = subprocess.run(
        cmd,
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    cli_command = (
        f"PYTHONPATH={src} python3 -m pigmeu_never_forget.cli "
        f"--config {config} {' '.join(args)}"
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"Command failed ({completed.returncode}): {stderr}")
    stdout = completed.stdout.strip()
    if not stdout:
        return cli_command, {}
    return cli_command, json.loads(stdout)


def run_pnf_mcp_tool(tool: str, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    repo = pnf_repo_path()
    config = config_path()
    cmd = [
        "python3",
        "-m",
        "pigmeu_never_forget.mcp.local_call",
        tool,
        "--config",
        str(config),
        "--payload",
        json.dumps(payload, ensure_ascii=True),
    ]
    env = dict(os.environ)
    src = repo / "src"
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src) if not existing_path else f"{src}:{existing_path}"
    completed = subprocess.run(
        cmd,
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    mcp_command = (
        f"PYTHONPATH={src} python3 -m pigmeu_never_forget.mcp.local_call "
        f"{tool} --config {config} --payload '{json.dumps(payload, ensure_ascii=True)}'"
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"MCP call failed ({completed.returncode}): {stderr}")
    stdout = completed.stdout.strip()
    if not stdout:
        return mcp_command, {}
    return mcp_command, json.loads(stdout)


def prefer_mcp() -> bool:
    return os.environ.get("PNF_PREFER_MCP", "1").strip() not in {"0", "false", "False"}


def run_with_mcp_fallback(
    mcp_tool: str,
    mcp_payload: dict[str, Any],
    cli_args: list[str],
) -> tuple[str, dict[str, Any], str]:
    if prefer_mcp():
        try:
            command, payload = run_pnf_mcp_tool(mcp_tool, mcp_payload)
            return command, payload, "mcp"
        except Exception:
            pass
    command, payload = run_pnf_cli(cli_args)
    return command, payload, "cli"


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
