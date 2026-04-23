# Error Playbook

- `SESSION_NOT_FOUND`: call `ensure_session.py` to create or recover the active session.
- `INVALID_REQUEST`: check that `session_stem` and payload JSON are valid.
- `PROJECT_NOT_FOUND`: verify the archive target project exists in the PNF workspace config.
- Archive failure: finalize the markdown file first, then retry `finalize_session.py` or `archive_session` after verifying PNF connectivity.
