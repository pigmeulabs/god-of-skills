#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: drawio_export.sh input.drawio --format png|svg|pdf|jpg [--embed] [--preview] [--scale 2] [--output file]" >&2
  exit 2
fi
INPUT="$1"; shift
FORMAT="png"; EMBED=0; PREVIEW=0; SCALE="2"; OUTPUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --format) FORMAT="$2"; shift 2 ;;
    --embed) EMBED=1; shift ;;
    --preview) PREVIEW=1; shift ;;
    --scale) SCALE="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
if [ ! -f "$INPUT" ]; then echo "Input not found: $INPUT" >&2; exit 1; fi
if [ -z "$OUTPUT" ]; then OUTPUT="${INPUT%.*}.${FORMAT}"; fi
BIN=""
for c in draw.io drawio /Applications/draw.io.app/Contents/MacOS/draw.io; do
  if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then BIN="$c"; break; fi
done
if [ -z "$BIN" ]; then
  echo "draw.io CLI not found. Install draw.io Desktop or use scripts/drawio_url.py fallback." >&2
  exit 127
fi
ARGS=("-x" "-f" "$FORMAT" "-o" "$OUTPUT" "$INPUT")
if [ "$PREVIEW" -eq 0 ] && [ "$EMBED" -eq 1 ]; then ARGS=("-x" "-f" "$FORMAT" "-e" "-o" "$OUTPUT" "$INPUT"); fi
if [ "$FORMAT" = "png" ] || [ "$FORMAT" = "jpg" ]; then ARGS=("-x" "-f" "$FORMAT" "-s" "$SCALE" "-o" "$OUTPUT" "$INPUT"); [ "$PREVIEW" -eq 0 ] && [ "$EMBED" -eq 1 ] && ARGS=("-x" "-f" "$FORMAT" "-e" "-s" "$SCALE" "-o" "$OUTPUT" "$INPUT"); fi
if command -v xvfb-run >/dev/null 2>&1 && [ -z "${DISPLAY:-}" ]; then
  xvfb-run -a --server-args="-screen 0 1280x1024x24" "$BIN" "${ARGS[@]}" --disable-gpu || "$BIN" "${ARGS[@]}" --disable-gpu --no-sandbox
else
  "$BIN" "${ARGS[@]}" --disable-gpu || "$BIN" "${ARGS[@]}" --disable-gpu --no-sandbox
fi
echo "Exported: $OUTPUT"
