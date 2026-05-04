#!/usr/bin/env python3
"""Lightweight layout checks for draw.io XML diagrams."""
import argparse
import itertools
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def fnum(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def rect(cell):
    g = cell.find("mxGeometry")
    if g is None:
        return None
    x, y = fnum(g.get("x")), fnum(g.get("y"))
    w, h = fnum(g.get("width")), fnum(g.get("height"))
    return x, y, w, h

def intersects(a, b, pad=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + pad <= bx or bx + bw + pad <= ax or ay + ah + pad <= by or by + bh + pad <= ay)

def contains(a, b, margin=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax - margin <= bx and ay - margin <= by and ax + aw + margin >= bx + bw and ay + ah + margin >= by + bh

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--min-width", type=float, default=30)
    p.add_argument("--min-height", type=float, default=20)
    p.add_argument("--overlap-pad", type=float, default=0)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--fix", action="store_true", help="Auto-fix negative coordinates by translating all elements")
    return p.parse_args()

def main():
    args = parse_args()
    root = ET.parse(args.file).getroot()
    models = []
    if root.tag == "mxfile":
        for d in root.findall("diagram"):
            models.extend([c for c in list(d) if c.tag == "mxGraphModel"])
    elif root.tag == "mxGraphModel":
        models.append(root)
    warnings = []
    for model in models:
        cells = []
        for c in model.findall("./root/mxCell"):
            if c.get("vertex") == "1":
                r = rect(c)
                if not r:
                    continue
                x, y, w, h = r
                cid = c.get("id", "?")
                if x < 0 or y < 0:
                    warnings.append(f"{cid}: negative coordinate ({x},{y})")
                if w < args.min_width or h < args.min_height:
                    warnings.append(f"{cid}: small shape {w}x{h}")
                cells.append((cid, c.get("value", ""), r))
                
        if args.fix:
            min_x = min([r[0] for _, _, r in cells] + [0])
            min_y = min([r[1] for _, _, r in cells] + [0])
            if min_x < 0 or min_y < 0:
                offset_x = -min_x + 20 if min_x < 0 else 0
                offset_y = -min_y + 20 if min_y < 0 else 0
                for c in model.findall("./root/mxCell"):
                    g = c.find("mxGeometry")
                    if g is not None:
                        if "x" in g.attrib:
                            g.set("x", str(fnum(g.get("x")) + offset_x))
                        if "y" in g.attrib:
                            g.set("y", str(fnum(g.get("y")) + offset_y))
                # Write changes back to file
                tree = ET.ElementTree(root)
                tree.write(args.file, encoding="utf-8", xml_declaration=False)
                print(f"Fixed negative coordinates by shifting X:+{offset_x} Y:+{offset_y}")
                # Reset warnings related to negative coords
                warnings = [w for w in warnings if "negative coordinate" not in w]

        for (a_id, a_label, a_rect), (b_id, b_label, b_rect) in itertools.combinations(cells, 2):
            if intersects(a_rect, b_rect, args.overlap_pad) and not contains(a_rect, b_rect) and not contains(b_rect, a_rect):
                warnings.append(f"possible overlap: {a_id} and {b_id}")
    for w in warnings:
        print("WARN:", w)
    if args.strict and warnings:
        print(f"Layout check failed: {len(warnings)} warnings")
        return 1
    print(f"OK: layout check completed with {len(warnings)} warnings")
    return 0

if __name__ == "__main__":
    sys.exit(main())
