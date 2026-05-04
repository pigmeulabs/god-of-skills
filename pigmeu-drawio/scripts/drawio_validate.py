#!/usr/bin/env python3
"""Validate draw.io XML source files for common agent-generation errors."""
import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EDGE_REQUIRED_GEOMETRY = "mxGeometry"

def parse_args():
    p = argparse.ArgumentParser(description="Validate draw.io XML")
    p.add_argument("file", help=".drawio file to validate")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    return p.parse_args()

def fail(msg):
    print(f"ERROR: {msg}")
    return False

def warn(msg, warnings):
    warnings.append(msg)
    print(f"WARN: {msg}")

def main():
    args = parse_args()
    path = Path(args.file)
    warnings = []
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    if "<!--" in text and re.search(r"<!--.*?--.*?-->", text, re.S):
        warn("xml comment appears to contain a double hyphen sequence", warnings)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        print(f"ERROR: invalid xml: {e}")
        return 1
    # Support either <mxfile> or bare <mxGraphModel>.
    models = []
    if root.tag == "mxfile":
        for diagram in root.findall("diagram"):
            for child in list(diagram):
                if child.tag == "mxGraphModel":
                    models.append(child)
    elif root.tag == "mxGraphModel":
        models.append(root)
    else:
        print(f"ERROR: root must be mxfile or mxGraphModel, got {root.tag}")
        return 1
    if not models:
        print("ERROR: no mxGraphModel found")
        return 1
    ids = set()
    ok = True
    modified = False
    for model_idx, model in enumerate(models, start=1):
        root_cell = model.find("root")
        if root_cell is None:
            warn(f"model {model_idx} has no <root>, auto-injecting", warnings)
            root_cell = ET.Element("root")
            for child in list(model):
                model.remove(child)
                root_cell.append(child)
            model.append(root_cell)
            modified = True
        cells = root_cell.findall("mxCell")
        cell_by_id = {}
        for c in cells:
            cid = c.get("id")
            if not cid:
                ok = fail("mxCell without id") and ok
                continue
            if cid in ids:
                ok = fail(f"duplicate id across diagrams: {cid}") and ok
            ids.add(cid)
            cell_by_id[cid] = c
        if "0" not in cell_by_id:
            warn("missing root cell id=0, auto-injecting", warnings)
            c0 = ET.Element("mxCell", id="0")
            root_cell.insert(0, c0)
            cell_by_id["0"] = c0
            ids.add("0")
            modified = True
        if "1" not in cell_by_id:
            warn("missing layer cell id=1, auto-injecting", warnings)
            c1 = ET.Element("mxCell", id="1", parent="0")
            root_cell.insert(1, c1)
            cell_by_id["1"] = c1
            ids.add("1")
            modified = True
            
        # ensure cells have a parent if they are not 0 or 1
        for cid, c in cell_by_id.items():
            if cid not in ("0", "1") and "parent" not in c.attrib:
                c.set("parent", "1")
                modified = True
        for cid, c in cell_by_id.items():
            is_edge = c.get("edge") == "1"
            is_vertex = c.get("vertex") == "1"
            if is_edge and is_vertex:
                ok = fail(f"cell {cid} cannot be both edge and vertex") and ok
            if is_edge:
                geom = c.find(EDGE_REQUIRED_GEOMETRY)
                if geom is None:
                    ok = fail(f"edge {cid} is missing mxGeometry") and ok
                elif geom.get("relative") != "1":
                    warn(f"edge {cid} geometry should use relative=1", warnings)
                if not c.get("source") or not c.get("target"):
                    warn(f"edge {cid} should usually define source and target", warnings)
            if is_vertex:
                geom = c.find("mxGeometry")
                if geom is None:
                    ok = fail(f"vertex {cid} is missing mxGeometry") and ok
                else:
                    for key in ("x", "y", "width", "height"):
                        if key not in geom.attrib:
                            warn(f"vertex {cid} geometry missing {key}", warnings)
            value = c.get("value")
            if value:
                html.unescape(value)  # parse smoke check
                style = c.get("style", "")
                if "fontFamily=" not in style and any(ch.isalpha() for ch in value):
                    warn(f"cell {cid} has text but no explicit fontFamily", warnings)
    if modified:
        ET.ElementTree(root).write(args.file, encoding="utf-8", xml_declaration=False)
        print(f"Auto-injected missing core structures into {path}")

    if not ok or (args.strict and warnings):
        print("Validation failed")
        return 1
    print(f"OK: {path} is valid draw.io XML ({len(ids)} cells, {len(warnings)} warnings)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
