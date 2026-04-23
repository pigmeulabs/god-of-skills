---
name: credentials-catalog
description: manage and retrieve local service credentials stored in a yaml catalog for the current environment. use when chatgpt needs to find credentials for a service, confirm whether credentials exist, add new credentials, update existing credentials, remove credentials, enforce file permissions, or ensure the credentials catalog path and gitignore rules are correct. supports read-only lookup for downstream tasks and confirmation-gated write operations on /home/chico/projects/.globals/credentials.yaml.
---

# Credentials Catalog

Manage the local credentials catalog stored at `/home/chico/projects/.globals/credentials.yaml`.

This skill has two responsibilities:
1. retrieve credentials needed by a user or another agent during a task;
2. add, update, or remove credential entries in a controlled way.

## Core rules

- Treat `/home/chico/projects/.globals/credentials.yaml` as the source of truth.
- Treat the catalog as plain-text local environment data exactly as specified by the project instructions.
- Use YAML with top-level key `services:` and one list item per service.
- Keep each service entry with `name` and `account`.
- Inside `account`, only use applicable fields from: `user`, `email`, `key`, `password`, `url`, `port`, `type`.
- Omit fields that do not apply.
- Preserve user-provided values exactly.
- Preserve service names exactly in storage.
- Use YAML safe serialization and keep the file human-readable.
- Before any write operation, show the exact intended change and ask for confirmation.
- For read-only lookup, do not ask for confirmation.
- Keep the file included in gitignore and keep permissions at `600`.
- If the file does not exist yet, create it with `services: []` before the first confirmed write.
- If ownership is not limited to `chico` or `root`, report it clearly; do not attempt privileged ownership changes.

## Operation routing

Identify the requested operation before doing anything else.

### 1. lookup credentials
Use this path when the user or another agent needs credentials for a service during a task.

Examples:
- "what are the postgres credentials?"
- "find the api key for service x"
- "i need the smtp account details"
- "use the credentials for redis in this task"

Workflow:
1. Read the catalog with `scripts/read_credentials.py`.
2. Match by this priority order: exact `name`, case-insensitive normalized `name`, exact account-field match (`user`, `email`, `url`, `port`, `type`), then partial contains on `name`.
3. If service name is ambiguous, search by account fields such as `user`, `email`, `url`, `port`, or `type`.
4. Return the smallest useful credential set for the task.
5. If multiple entries plausibly match, list candidate service names, include one distinguishing field (`url`, `type`, or `user`), and ask which one to use.
6. If no match is found, say so clearly.

### 2. add credentials
Use this path when the user wants to create a new service entry.

Workflow:
1. Collect missing fields needed for the new entry.
2. Build a proposed YAML entry.
3. Show the exact proposed entry back to the user.
4. Ask for confirmation.
5. After confirmation, run `scripts/write_credentials.py add ...`.
6. Run `scripts/ensure_catalog_security.py`.
7. Report the result and the path updated.

### 3. update credentials
Use this path when the user wants to change one or more fields on an existing service.

Workflow:
1. Read the catalog and identify the target entry.
2. If multiple services are similar, disambiguate before editing.
3. Build the proposed updated entry and describe changed fields only.
4. Show the exact before/after or changed fields.
5. Ask for confirmation.
6. After confirmation, run `scripts/write_credentials.py update ...`.
7. Run `scripts/ensure_catalog_security.py`.
8. Report the result.

### 4. remove credentials
Use this path when the user wants to delete an existing service entry.

Workflow:
1. Read the catalog and identify the entry to remove.
2. Show the exact service that will be removed.
3. Ask for confirmation.
4. After confirmation, run `scripts/write_credentials.py remove ...`.
5. Run `scripts/ensure_catalog_security.py`.
6. Report the result.

### 5. ensure catalog setup
Use this path when the task is to create, validate, or repair the catalog itself.

Workflow:
1. Run `scripts/ensure_catalog_security.py`.
2. Confirm the file exists, permissions are `600`, and `.gitignore` contains the catalog path.
3. Report any ownership issue without attempting privileged changes.

## How to identify the right credential entry

Always identify entries using this priority order:
1. exact service name match;
2. normalized service name match ignoring case and extra spaces;
3. exact account details match (`user`, `email`, `url`, `port`, `type`);
4. partial contains match on service name.

When choosing what to return to another agent or task:
- prefer the exact fields required by the task;
- do not invent missing values;
- if the task needs only a username and password, return only those plus the service name unless the url or port is necessary;
- if a field is missing, say it is absent from the catalog.
- follow this minimal output policy when practical:
  - database login: `user`, `password`, `url`, `port`, `type`
  - api call: `key`, `url`, `type`
  - smtp: `user`, `password`, `url`, `port`, `type`

## Confirmation protocol for write operations

Before adding, updating, or removing credentials, always present:
- target service name;
- exact fields to be added, changed, or removed;
- resulting YAML fragment when practical.

Use plain, direct wording such as:
"I found the target entry below. Confirm that I should apply this change to `/home/chico/projects/.globals/credentials.yaml`."

Do not perform the write until the user explicitly confirms.

## Scripts

Use these scripts directly when applicable:
- `scripts/read_credentials.py` for structured lookup and catalog inspection
- `scripts/write_credentials.py` for add, update, and remove operations
- `scripts/ensure_catalog_security.py` to create the file if missing, enforce `600`, and ensure `.gitignore` contains the catalog path

## References

Consult these files when needed:
- `references/catalog-spec.md` for the canonical catalog structure and examples
- `references/lookup-and-matching.md` for lookup rules and disambiguation behavior
- `references/write-operation-examples.md` for concrete add, update, and remove confirmation examples
- `references/security-and-file-rules.md` for file path, permissions, and gitignore rules

## Output guidance

For lookup requests:
- return the matching service and the relevant account fields in a compact YAML or bulletless plain-text block;
- mention missing fields explicitly.

For write requests:
- first return the proposed change;
- ask for confirmation;
- after confirmation, return the status of the operation and the affected path.

## Credential Rotation

Use this path when the task requires loading or rotating API keys across multiple accounts for the same provider (Mistral or Groq).

### Operation: load rotated key

Returns the next key in round-robin for a provider, advancing the cursor in the state file.

```bash
python3 scripts/cred-rotate.py next mistral
python3 scripts/cred-rotate.py next groq
```

### Operation: load into shell session

```bash
source scripts/load-api-keys.sh
```

### Operation: inspect rotation state

```bash
python3 scripts/cred-rotate.py status
```

### Operation: reset cursor

```bash
python3 scripts/cred-rotate.py reset mistral
```

### State file

`$CREDENTIALS_CATALOG_DIR/credential-rotation-state.json`
Default: `/home/chico/projects/.globals/credential-rotation-state.json`

### References

- `references/credential-rotation.md` — full documentation
- `scripts/cred-rotate.py` — CLI implementation
- `scripts/load-api-keys.sh` — shell wrapper for Mistral + Groq
