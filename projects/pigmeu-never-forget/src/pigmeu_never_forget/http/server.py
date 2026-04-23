"""HTTP server runner for the FastAPI adapter."""

from __future__ import annotations

from pigmeu_never_forget.http.api import create_http_app


def run_http_server(
    config_path: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8787,
) -> None:
    """Run the FastAPI server with uvicorn."""
    try:
        import uvicorn
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("uvicorn is not installed. Install with `pip install \".[api]\"`.") from exc

    app = create_http_app(config_path=config_path)
    uvicorn.run(app, host=host, port=port)

