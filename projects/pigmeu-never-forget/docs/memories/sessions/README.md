# Session Memories

Use this folder for compact session memory files:

- `<stem>/<stem>.md`, where `<stem>` follows `AA-MM-DD-HH-MM-session-ID`

Recommended sections:

- Objective
- Relevant context
- Decisions
- Actions/results
- Pending items and next steps

File layout:

- The session metadata is stored in a JSON block at the top of the Markdown file.
- The human-readable body follows the metadata block and is regenerated on each turn.
- Each session keeps a single file inside its own folder, using the same stem for both.

Operational rule:

- Finalize the file at session end or when the session becomes stale for 8 hours, then archive it with `pnf-session-memory`.
