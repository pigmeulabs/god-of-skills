#!/usr/bin/env python3
"""Run evaluation cases for the pigmeu-drawio skill."""
import json
import subprocess
import sys
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    evals_dir = base_dir / "evals"
    
    cases = []
    for eval_file in evals_dir.glob("*.json"):
        with open(eval_file) as f:
            data = json.load(f)
            if "cases" in data:
                cases.extend(data["cases"])
                
    print(f"Found {len(cases)} evaluation cases in {evals_dir}")
    print("Note: Automated LLM generation requires OpenCode CLI integration.")
    
    for idx, case in enumerate(cases, 1):
        print(f"\n[{idx}/{len(cases)}] Case: {case.get('id', 'unknown')}")
        print(f"Prompt: {case.get('prompt', '')}")
        print(f"Expect: {', '.join(case.get('expect', []))}")
        
    print("\nTo validate generated diagrams, use:")
    print("  python3 scripts/drawio_validate.py <output.drawio>")
    return 0

if __name__ == "__main__":
    sys.exit(main())
