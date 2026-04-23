"""MCP server for session memory storage."""

from __future__ import annotations

import argparse
import os

from pigmeu_never_forget.session_memory.adapter import SessionMemoryAdapter


def _build_session_mcp(config_path: str | None = None):
    from mcp.server.fastmcp import FastMCP

    adapter = SessionMemoryAdapter(config_path=config_path)
    mcp = FastMCP("pnf-session-memory")

    @mcp.tool()
    def start_session(payload: dict | None = None, request_id: str | None = None):
        return adapter.start_session(payload or {}, request_id=request_id)

    @mcp.tool()
    def append_turn(payload: dict | None = None, request_id: str | None = None):
        return adapter.append_turn(payload or {}, request_id=request_id)

    @mcp.tool()
    def update_metrics(payload: dict | None = None, request_id: str | None = None):
        return adapter.update_metrics(payload or {}, request_id=request_id)

    @mcp.tool()
    def finalize_session(payload: dict | None = None, request_id: str | None = None):
        return adapter.finalize_session(payload or {}, request_id=request_id)

    @mcp.tool()
    def archive_session(payload: dict | None = None, request_id: str | None = None):
        return adapter.archive_session(payload or {}, request_id=request_id)

    @mcp.tool()
    def record_response(payload: dict | None = None, request_id: str | None = None):
        return adapter.record_response(payload or {}, request_id=request_id)

    @mcp.tool()
    def rollover_stale_sessions(payload: dict | None = None, request_id: str | None = None):
        return adapter.rollover_stale_sessions(payload or {}, request_id=request_id)

    @mcp.tool()
    def get_session_status(payload: dict | None = None, request_id: str | None = None):
        return adapter.get_session_status(payload or {}, request_id=request_id)

    @mcp.tool()
    def latest_session(request_id: str | None = None):
        return adapter.latest_session(request_id=request_id)

    return mcp


def run_stdio_server(config_path: str | None = None) -> None:
    try:
        mcp = _build_session_mcp(config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Failed to start session memory MCP server. Install MCP SDK (`pip install mcp`) and validate config."
        ) from exc
    mcp.run()


def main() -> int:
    parser = argparse.ArgumentParser(prog="pnf-session-mcp")
    parser.add_argument("--config", help="Optional workspace config path.")
    args = parser.parse_args()
    run_stdio_server(config_path=args.config or os.environ.get("PNF_CONFIG_PATH"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
