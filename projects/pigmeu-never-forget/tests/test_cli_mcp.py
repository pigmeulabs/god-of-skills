from __future__ import annotations

from pigmeu_never_forget.cli import build_parser


def test_cli_accepts_mcp_serve_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["mcp-serve"])
    assert args.command == "mcp-serve"
    assert args.mcp_config is None


def test_cli_accepts_index_text_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["index-text", "project-a", "note-1", "hello"])
    assert args.command == "index-text"
    assert args.project_id == "project-a"
    assert args.title == "note-1"
    assert args.text == "hello"


def test_cli_accepts_job_status_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["job-status", "project-a", "job_1"])
    assert args.command == "job-status"
    assert args.project_id == "project-a"
    assert args.job_id == "job_1"


def test_cli_accepts_api_serve_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["api-serve", "--host", "0.0.0.0", "--port", "9000"])
    assert args.command == "api-serve"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
