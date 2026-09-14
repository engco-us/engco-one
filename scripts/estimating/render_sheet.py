#!/usr/bin/env python3
"""Render one PDF page to an image for vision reading — the ONLY sanctioned
way to get a sheet in front of a vision model in this pipeline. Exists so
every render uses the same, tested settings instead of each run picking an
arbitrary DPI (too low: illegible; too high: wastes tokens for no benefit,
since drawing text at real CD scale doesn't get more readable past a point).

See VISION RULE in scripts/estimating/README.md before using an image this
produces: vision counts and identifies, it never originates a precise
number that belongs in a schedule.

Usage:
  python3 render_sheet.py "01 23015 CIVIL Permit.pdf" 18 --out renders/civil-p18.png
"""
import argparse
import subprocess
from pathlib import Path

DEFAULT_DPI = 100  # tested: legible for plan-level counting/identification
                    # without producing an unusably huge image for a 24x36 sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("page", type=int)
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    ap.add_argument("--out", required=True, help="Output PNG path (without extension; pdftoppm appends -N.png)")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stem = str(out_path.with_suffix(""))

    subprocess.run([
        "pdftoppm", "-png", "-f", str(args.page), "-l", str(args.page),
        "-r", str(args.dpi), args.pdf, stem,
    ], check=True)

    # pdftoppm names single-page output "<stem>-<page>.png" (or just
    # "<stem>.png" for some versions on a single-page range) — report both
    # possibilities so the caller knows exactly what to open next.
    candidates = [f"{stem}-{args.page}.png", f"{stem}-{args.page:02d}.png", f"{stem}.png"]
    found = [c for c in candidates if Path(c).exists()]
    if found:
        print(f"Rendered: {found[0]}")
    else:
        print(f"Rendered (check {out_path.parent} for the exact filename pdftoppm chose)")


if __name__ == "__main__":
    main()
