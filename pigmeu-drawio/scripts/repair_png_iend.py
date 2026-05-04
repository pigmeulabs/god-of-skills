#!/usr/bin/env python3
"""Ensure a PNG ends with a valid IEND chunk. Safe and idempotent."""
import argparse
import sys
from pathlib import Path
IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"
SIG = b"\x89PNG\r\n\x1a\n"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    args = p.parse_args()
    path = Path(args.file)
    data = path.read_bytes()
    if not data.startswith(SIG):
        print(f"ERROR: not a PNG file: {path}")
        return 1
    idx = data.rfind(IEND)
    if idx >= 0 and idx + len(IEND) == len(data):
        print(f"OK: {path} already has valid terminal IEND")
        return 0
    if idx >= 0:
        data = data[:idx]
    path.write_bytes(data + IEND)
    print(f"OK: repaired terminal IEND for {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
