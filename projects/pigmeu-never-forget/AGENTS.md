# AGENTS.md

## Scope and truth
- Keep this file minimal and stable. Put long procedures in `docs/`.
- When prose conflicts with code, trust `pyproject.toml` and `src/pigmeu_never_forget/`.
- Canonical repository root: `/home/ubuntu/projects-workspace/god-of-skills`.
- OpenCode runtime under `/home/ubuntu/projects-workspace/.opencode/` is an installed mirror, not the source of truth.
- Runtime state is generated: `_workspace/` and every project `.rag/`.

## Token-efficiency rules
- Prefer short, direct outputs by default.
- Include only context needed for the current task.
- Reference files/commands instead of pasting large content.
- Add new instructions only after recurring mistakes; avoid speculative rules.
- If a rule grows beyond quick-scan size, move details to `docs/` and keep a pointer here.

## Context policy
- Keep active context to: objective, constraints, decisions, pending items, next step.
- Summarize old conversation state instead of replaying full history.
- For session memory artifacts, use `docs/memories/sessions/<stem>/<stem>.md` where `<stem>` follows `AA-MM-DD-HH-MM-session-ID`.
- After each assistant response, record the turn using `pnf-session-memory.record_response` or the installed mirror `python3 /home/ubuntu/projects-workspace/.opencode/skills/pnf-session-memory-ops/scripts/record_response.py --payload '{...}'`.
- On session close, always run `finalize_session` with archive enabled.
- Session files must include:
  - objective
  - key decisions
  - actions and results
  - pending risks/next steps
  - structured JSON metadata block at the top of the file

## Project quick map
- Python 3.11+ with `src/` layout.
- Workspace discovery scans immediate child directories as projects.
- Per project: `.rag/project.yaml`, `.rag/state.db`, `.rag/memory.db`, `.rag/cache/`, `.rag/logs/`.
- `project_id` is folder slug.

## Operating flow (PNF)
- Preferred interface order:
  1. MCP: `pnf-mcp` tools/resources.
  2. CLI fallback: `python3 -m pigmeu_never_forget.cli ...`.
  3. HTTP fallback for integrations.
- Standard sequence:
  1. `sync_project`
  2. `search_project`
  3. `ask_project`
  4. `get_project_stats` / `get_job_status`
  5. `consolidate_project` when memory refresh is needed

## MCP and skills (OpenCode)
- Core MCP:
  - `pnf-mcp` for indexing/retrieval/ask/stats/jobs/consolidation.
- Optional support MCPs (if connected):
  - `token-savior-recall` for structure-first navigation.
  - `context-mode` for context shaping.
- Skill selection:
  - `pnf-pigmeu-copilot-ops`: routine ops for `pigmeu-copilot`.
  - `pnf-session-memory-ops`: session persistence, rollover, and archive.
  - `python-expert`: implementation, refactor, tests.
  - `rag-architect`: ingest/chunk/retrieval/memory design.
  - `skill-creator`: create/update skills.
  - `skill-installer`: install curated skills.
  - `credentials-catalog`: local credential catalog operations.

## Commands
- Tests: `pytest -q`
- CLI from source: `PYTHONPATH=src python3 -m pigmeu_never_forget.cli <command>`
- MCP server: `PYTHONPATH=src python3 -m pigmeu_never_forget.cli mcp-serve`
- Session MCP: `PYTHONPATH=src python3 -m pigmeu_never_forget.session_memory.server --config <config>`
- Session CLI helper: `pnf-session record-response --payload '{...}'`
- HTTP server: `PYTHONPATH=src python3 -m pigmeu_never_forget.cli api-serve --host 127.0.0.1 --port 8787`
- Health check: `opencode mcp list` (expect `pnf-mcp` and `pnf-session-memory` connected)

## Error playbook
- `PROJECT_NOT_FOUND`: run workspace init/discovery; confirm folder slug.
- `PROJECT_LOCKED`: wait/retry; check active job.
- `no such table:*`: missing bootstrap/migrations; run `bootstrap-project` then `sync`.
- MCP disconnected: validate `.opencode/opencode.json` command path and recheck `opencode mcp list`.

## Keep docs synced
- If CLI/MCP/API behavior changes, update:
  - `/home/ubuntu/projects-workspace/god-of-skills/README.md`
  - `README.md`
  - `docs/implementation-status.md`
  - `docs/api-contracts.md` (when contracts/envelopes change)
  - `/home/ubuntu/projects-workspace/god-of-skills/docs/skills/*.md` and `/home/ubuntu/projects-workspace/god-of-skills/docs/mcps/*.md` when operational behavior changes
