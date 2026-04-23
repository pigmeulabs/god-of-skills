#!/usr/bin/env python3
"""
cred-rotate.py — Credential rotation CLI for Mistral and Groq.

Usage:
    python3 cred-rotate.py get <service>          Print active key (no advance)
    python3 cred-rotate.py next <service>         Advance cursor and print key
    python3 cred-rotate.py next <service> --export  Print as export VAR="..."
    python3 cred-rotate.py status                 Show cursor state for all services
    python3 cred-rotate.py reset <service>        Reset cursor to 0
"""

import json
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
import os

# ── paths ──────────────────────────────────────────────────────────────────────
GLOBALS_DIR   = Path(os.environ.get("CREDENTIALS_CATALOG_DIR", "/home/chico/projects/.globals"))
CATALOG_PATH  = GLOBALS_DIR / "credentials.yaml"
STATE_PATH    = GLOBALS_DIR / "credential-rotation-state.json"

# ── service config ─────────────────────────────────────────────────────────────
SERVICES = {
    "mistral": {
        "env_var": "MISTRAL_API_KEY",
        "prefix":  "mistral",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "prefix":  "groq",
    },
}


# ── helpers ───────────────────────────────────────────────────────────────────

def load_catalog() -> dict:
    with CATALOG_PATH.open() as f:
        return yaml.safe_load(f)


def get_keys_for_service(catalog: dict, service: str) -> list[dict]:
    prefix = SERVICES[service]["prefix"]
    keys = []
    for entry in catalog.get("services", []):
        if entry["name"].startswith(prefix + "-"):
            acct = entry.get("account", {})
            api_key = acct.get("key") or acct.get("access_token")
            if api_key:
                keys.append({"name": entry["name"], "key": api_key})
    return keys


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"version": 1, "services": {}}
    with STATE_PATH.open() as f:
        return json.load(f)


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    STATE_PATH.chmod(0o600)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_service_state(state: dict, service: str) -> dict:
    return state["services"].setdefault(service, {
        "cursor": 0,
        "last_key": "",
        "updated_at": "",
    })


# ── commands ───────────────────────────────────────────────────────────────────

def cmd_get(service: str, export: bool = False) -> None:
    """Return the current active key without advancing the cursor."""
    catalog = load_catalog()
    keys = get_keys_for_service(catalog, service)
    if not keys:
        _die(f"No keys found for service '{service}'.")

    state = load_state()
    svc   = get_service_state(state, service)
    idx   = svc["cursor"] % len(keys)
    entry = keys[idx]

    if export:
        env_var = SERVICES[service]["env_var"]
        print(f'export {env_var}="{entry["key"]}"')
    else:
        print(entry["key"])


def cmd_next(service: str, export: bool = False) -> None:
    """Advance cursor by one and return the new active key."""
    catalog = load_catalog()
    keys = get_keys_for_service(catalog, service)
    if not keys:
        _die(f"No keys found for service '{service}'.")

    state = load_state()
    svc   = get_service_state(state, service)

    # advance
    svc["cursor"]     = (svc["cursor"] + 1) % len(keys)
    svc["last_key"]   = keys[svc["cursor"]]["name"]
    svc["updated_at"] = now_iso()
    save_state(state)

    entry = keys[svc["cursor"]]

    if export:
        env_var = SERVICES[service]["env_var"]
        print(f'export {env_var}="{entry["key"]}"')
    else:
        print(entry["key"])


def cmd_status() -> None:
    """Show rotation state for all services."""
    catalog = load_catalog()
    state   = load_state()

    for service in SERVICES:
        keys = get_keys_for_service(catalog, service)
        svc  = get_service_state(state, service)
        idx  = svc["cursor"] % len(keys) if keys else 0

        active_name = keys[idx]["name"] if keys else "—"
        print(f"[{service.upper()}]")
        print(f"  active key : {active_name}")
        print(f"  cursor     : {svc['cursor']} / {len(keys)} total")
        print(f"  last used  : {svc['last_key'] or '—'}")
        print(f"  updated_at : {svc['updated_at'] or '—'}")
        print()


def cmd_reset(service: str) -> None:
    """Reset cursor to 0 for a service."""
    state = load_state()
    svc   = get_service_state(state, service)
    svc["cursor"]     = 0
    svc["last_key"]   = ""
    svc["updated_at"] = now_iso()
    save_state(state)
    print(f"Cursor for '{service}' reset to 0.")


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "status":
        cmd_status()
        return

    if cmd in ("get", "next"):
        if len(args) < 2:
            _die(f"Usage: cred-rotate.py {cmd} <service>")
        service = args[1].lower()
        if service not in SERVICES:
            _die(f"Unknown service '{service}'. Choose: {', '.join(SERVICES)}")
        export = "--export" in args

        if cmd == "get":
            cmd_get(service, export)
        else:
            cmd_next(service, export)
        return

    if cmd == "reset":
        if len(args) < 2:
            _die("Usage: cred-rotate.py reset <service>")
        service = args[1].lower()
        if service not in SERVICES:
            _die(f"Unknown service '{service}'. Choose: {', '.join(SERVICES)}")
        cmd_reset(service)
        return

    _die(f"Unknown command '{cmd}'. Run without arguments for help.")


if __name__ == "__main__":
    main()
