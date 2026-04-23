"""Local MCP server exposing pigmeu-never-forget operations."""

from __future__ import annotations

from pigmeu_never_forget.mcp.adapter import PNFMCPAdapter


def _build_mcp_server(config_path: str | None = None):
    """Build MCP server instance and register tools/resources."""
    from mcp.server.fastmcp import FastMCP

    adapter = PNFMCPAdapter(config_path=config_path)
    mcp = FastMCP("pnf-mcp")

    @mcp.tool()
    def list_projects(request_id: str | None = None):
        return adapter.list_projects(request_id=request_id)

    @mcp.tool()
    def sync_project(
        project_id: str,
        mode: str = "incremental",
        force: bool = False,
        request_id: str | None = None,
    ):
        return adapter.sync_project(project_id, mode=mode, force=force, request_id=request_id)

    @mcp.tool()
    def index_text(
        project_id: str,
        title: str,
        text: str,
        source_type: str = "inline_text",
        tags: list[str] | None = None,
        request_id: str | None = None,
    ):
        return adapter.index_text(
            project_id=project_id,
            title=title,
            text=text,
            source_type=source_type,
            tags=tags,
            request_id=request_id,
        )

    @mcp.tool()
    def search_project(
        project_id: str,
        query: str,
        top_k: int = 8,
        expand: bool = False,
        request_id: str | None = None,
    ):
        return adapter.search_project(
            project_id=project_id,
            query=query,
            top_k=top_k,
            expand=expand,
            request_id=request_id,
        )

    @mcp.tool()
    def ask_project(
        project_id: str,
        question: str,
        top_k: int = 6,
        allow_summary_only: bool = True,
        request_id: str | None = None,
    ):
        return adapter.ask_project(
            project_id=project_id,
            question=question,
            top_k=top_k,
            allow_summary_only=allow_summary_only,
            request_id=request_id,
        )

    @mcp.tool()
    def get_project_stats(project_id: str, request_id: str | None = None):
        return adapter.get_project_stats(project_id=project_id, request_id=request_id)

    @mcp.tool()
    def consolidate_project(
        project_id: str,
        mode: str = "incremental",
        request_id: str | None = None,
    ):
        return adapter.consolidate_project(project_id=project_id, mode=mode, request_id=request_id)

    @mcp.tool()
    def get_job_status(project_id: str, job_id: str, request_id: str | None = None):
        return adapter.get_job_status(project_id=project_id, job_id=job_id, request_id=request_id)

    @mcp.resource("rag://projects")
    def rag_projects() -> str:
        return adapter.resource_projects()

    @mcp.resource("rag://project/{project_id}/summary")
    def rag_project_summary(project_id: str) -> str:
        return adapter.resource_project_summary(project_id)

    @mcp.resource("rag://project/{project_id}/stats")
    def rag_project_stats(project_id: str) -> str:
        return adapter.resource_project_stats(project_id)

    @mcp.resource("rag://project/{project_id}/jobs/{job_id}")
    def rag_project_job(project_id: str, job_id: str) -> str:
        return adapter.resource_project_job(project_id, job_id)

    return mcp


def run_stdio_server(config_path: str | None = None) -> None:
    """Run MCP server over stdio transport."""
    try:
        mcp = _build_mcp_server(config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Failed to start MCP server. Install MCP SDK (`pip install mcp`) and validate config."
        ) from exc
    mcp.run()

