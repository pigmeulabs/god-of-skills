"""CLI entrypoints for the foundation implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pigmeu_never_forget.app import create_application


def build_parser() -> argparse.ArgumentParser:
    """Build the root CLI parser."""
    parser = argparse.ArgumentParser(prog="pnf")
    parser.add_argument("--config", help="Path to workspace config file.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-workspace", help="Create workspace metadata files.")
    subparsers.add_parser("discover", help="Discover projects in the workspace.")

    bootstrap = subparsers.add_parser(
        "bootstrap-project",
        help="Initialize a project .rag structure.",
    )
    bootstrap.add_argument("project_path", help="Absolute or relative project path.")

    sync = subparsers.add_parser("sync", help="Run incremental sync for a project.")
    sync.add_argument("project_id", help="Project id or folder name.")

    search = subparsers.add_parser("search", help="Search project knowledge.")
    search.add_argument("project_id", help="Project id or folder name.")
    search.add_argument("query", help="Search query.")
    search.add_argument("--top-k", type=int, default=8, help="Number of hits.")

    index_text = subparsers.add_parser("index-text", help="Index inline text into project knowledge.")
    index_text.add_argument("project_id", help="Project id or folder name.")
    index_text.add_argument("title", help="Inline title identifier.")
    index_text.add_argument("text", help="Inline text payload.")
    index_text.add_argument("--source-type", default="inline_text", help="Source type label.")

    ask = subparsers.add_parser("ask", help="Ask a grounded question to a project.")
    ask.add_argument("project_id", help="Project id or folder name.")
    ask.add_argument("question", help="Question text.")
    ask.add_argument("--top-k", type=int, default=6, help="Number of hits.")

    consolidate = subparsers.add_parser(
        "consolidate",
        help="Run memory consolidation for a project.",
    )
    consolidate.add_argument("project_id", help="Project id or folder name.")

    stats = subparsers.add_parser("stats", help="Get project stats.")
    stats.add_argument("project_id", help="Project id or folder name.")

    job_status = subparsers.add_parser("job-status", help="Get a project job status.")
    job_status.add_argument("project_id", help="Project id or folder name.")
    job_status.add_argument("job_id", help="Job id.")

    mcp = subparsers.add_parser("mcp-serve", help="Run local MCP server over stdio.")
    mcp.add_argument("--config", dest="mcp_config", help="Optional workspace config path.")

    api = subparsers.add_parser("api-serve", help="Run HTTP API server.")
    api.add_argument("--host", default="127.0.0.1", help="Host interface.")
    api.add_argument("--port", default=8787, type=int, help="HTTP port.")
    api.add_argument("--config", dest="api_config", help="Optional workspace config path.")

    return parser


def main() -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    workspace_service = create_application(args.config)

    if args.command == "init-workspace":
        result = workspace_service.initialize_workspace()
    elif args.command == "discover":
        result = workspace_service.discover_projects()
    elif args.command == "bootstrap-project":
        result = workspace_service.initialize_project(Path(args.project_path))
    elif args.command == "sync":
        result = workspace_service.sync_project(args.project_id)
    elif args.command == "search":
        result = workspace_service.search_project(args.project_id, args.query, top_k=args.top_k)
    elif args.command == "index-text":
        result = workspace_service.index_text(
            args.project_id,
            args.title,
            args.text,
            source_type=args.source_type,
        )
    elif args.command == "ask":
        result = workspace_service.ask_project(args.project_id, args.question, top_k=args.top_k)
    elif args.command == "consolidate":
        result = workspace_service.consolidate_project(args.project_id)
    elif args.command == "stats":
        result = workspace_service.get_project_stats(args.project_id)
    elif args.command == "job-status":
        result = workspace_service.get_job_status(args.project_id, args.job_id)
    elif args.command == "mcp-serve":
        from pigmeu_never_forget.mcp.server import run_stdio_server

        run_stdio_server(config_path=args.mcp_config or args.config)
        return 0
    elif args.command == "api-serve":
        from pigmeu_never_forget.http.server import run_http_server

        run_http_server(
            config_path=args.api_config or args.config,
            host=args.host,
            port=args.port,
        )
        return 0
    else:
        parser.error(f"Unsupported command: {args.command}")
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
