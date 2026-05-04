#!/usr/bin/env python3
"""Generate diagrams.net editor/viewer fallback URLs from uncompressed draw.io XML."""
import argparse
import base64
import sys
import urllib.parse
import zlib
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--mode", choices=["editor", "viewer"], default="editor")
    p.add_argument("--page", default="0")
    return p.parse_args()

def encode_drawio_xml(xml_text):
    compressed = zlib.compressobj(level=9, wbits=-15)
    data = compressed.compress(xml_text.encode("utf-8")) + compressed.flush()
    return urllib.parse.quote(base64.b64encode(data).decode("ascii"), safe="")

def main():
    args = parse_args()
    xml = Path(args.file).read_text(encoding="utf-8")
    payload = encode_drawio_xml(xml)
    if args.mode == "viewer":
        url = f"https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1#R{payload}"
    else:
        url = f"https://app.diagrams.net/?client=1&libs=general;uml;bpmn&create={Path(args.file).name}#R{payload}"
    print(url)
    return 0

if __name__ == "__main__":
    sys.exit(main())
