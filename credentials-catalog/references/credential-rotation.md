# Credential Rotation

## Overview

The credential rotation system provides round-robin key selection across multiple API keys for the same provider. State is persisted between sessions so each new session uses a different key.

## Supported providers

| Provider | Keys in rotation | State key |
|----------|-----------------|-----------|
| Mistral  | all `mistral-*` entries in `credentials.yaml` | `mistral` |
| Groq     | all `groq-*` entries in `credentials.yaml`    | `groq`    |

## State file

`$CREDENTIALS_CATALOG_DIR/credential-rotation-state.json` (default: `/home/chico/projects/.globals/credential-rotation-state.json`)

```json
{
  "version": 1,
  "services": {
    "mistral": { "cursor": 0, "last_key": "", "updated_at": "" },
    "groq":    { "cursor": 0, "last_key": "", "updated_at": "" }
  }
}
```

## CLI — `scripts/cred-rotate.py`

| Command | Description |
|---------|-------------|
| `python3 cred-rotate.py get <service>` | Returns active key without advancing cursor |
| `python3 cred-rotate.py next <service>` | Advances cursor and returns next key |
| `python3 cred-rotate.py next <service> --export` | Emits `export VAR="key"` for shell eval |
| `python3 cred-rotate.py status` | Shows cursor state for all services |
| `python3 cred-rotate.py reset <service>` | Resets cursor to 0 |

## Shell integration — `scripts/load-api-keys.sh`

Sources `MISTRAL_API_KEY` and `GROQ_API_KEY` into the current session with rotation:

```bash
source scripts/load-api-keys.sh
```

## Environment variable

Set `CREDENTIALS_CATALOG_DIR` to override the default globals path:

```bash
export CREDENTIALS_CATALOG_DIR=/path/to/globals
source scripts/load-api-keys.sh
```

## Integration with kairon-mesh
`kairon-mesh/scripts/load-api-keys.sh` delegates to this skill's `cred-rotate.py`.
