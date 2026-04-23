# Workflow

1. Call `ensure_session.py`.
2. After every assistant response, call `record_response.py` with the prompt, response, model, agent, tools, metrics, and changed files when available.
3. Call `status.py` whenever you need to inspect the active session.
4. Call `finalize_session.py` on session close or when the active session becomes stale.
5. Let the session MCP archive the markdown into the configured PNF project.
