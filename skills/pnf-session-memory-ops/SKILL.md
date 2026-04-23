---
name: pnf-session-memory-ops
description: Persist session turns in docs/memories/sessions and archive finalized sessions with pigmeu-never-forget. Use when you need a running chat log, stale-session rollover, or long-term memory storage for the current workspace session.
---

# PNF Session Memory Ops

Use this skill to keep a markdown session file updated during an OpenCode session.

## Default flow

1. Ensure there is an active session:
```bash
python3 scripts/ensure_session.py
```
2. Record the current assistant response (auto-ensures active session and rolls over stale sessions):
```bash
python3 scripts/record_response.py --payload '{"prompt":"...","response":"...","model":"..."}'
```
3. Check status:
```bash
python3 scripts/status.py --session-stem "..."
```
4. Finalize and archive when the session ends:
```bash
python3 scripts/finalize_session.py --session-stem "..."
```

## Operating rules

- Prefer MCP first via `pnf-session-memory`; use CLI fallback when MCP is unavailable.
- Keep one markdown file per session in `docs/memories/sessions/<stem>/<stem>.md`.
- Rollover stale sessions after 8 hours of inactivity.
- Store unknown token metrics as `null` instead of inventing values.
- Include changed files, tools, skills, MCPs, agents, humans, and turn text in the session file.

## Environment

- `PNF_REPO_PATH`: root of `pigmeu-never-forget`
- `PNF_CONFIG_PATH`: workspace config used by the PNF archive step
- `PNF_SESSION_PREFER_MCP`: `1` by default
- `PNF_SESSION_ARCHIVE_PROJECT_ID`: archive target project id

## References

- `references/workflow.md`
- `references/error-playbook.md`
