# Security And File Rules

## Required file rules
- File path: `/home/chico/projects/.globals/credentials.yaml`
- File mode: `600`
- Intended owners: `chico` and `root`
- Store credentials in plain text exactly as specified by the project instructions.

## Gitignore rule
Ensure the catalog path is ignored by git. If a repository `.gitignore` is available, append the exact path line when missing.

Suggested ignore line:
```text
/home/chico/projects/.globals/credentials.yaml
```

If only a project-root `.gitignore` is appropriate in the current environment, add a path that correctly ignores the file from that repository root.

## Ownership handling
This skill may inspect ownership.
If ownership is not restricted to `chico` or `root`, report the issue clearly.
Do not attempt privileged ownership changes.
