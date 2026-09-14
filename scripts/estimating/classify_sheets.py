#!/usr/bin/env python3
"""Classify every page of a discipline PDF (permit set, CD set) by sheet
type, so an estimator (human or agent) knows exactly which page has the
data they need instead of paging through a 70-sheet set by hand.

This mechanizes what a real takeoff always starts with: find the code
summary, find the schedules, find the framing plans. Deterministic keyword
matching only — no model call, no cost, no chance of inventing a sheet
that isn't there. If a PDF page has no extractable text (a raster scan),
it's reported as unclassified rather than guessed at.

Usage:
  python3 classify_sheets.py "03 23015 ARCH Permit.pdf" --discipline architectural --out manifest.json
  python3 classify_sheets.py "01 23015 CIVIL Permit.pdf" --discipline civil
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

# Ordered: more specific patterns first so e.g. "ROOF FRAMING PLAN" doesn't
# get miscategorized as a generic "FLOOR PLAN".
SHEET_TYPE_PATTERNS = [
    ("code_summary", r"OCCUPANCY LOAD|GROSS BUILDING AREA|ALLOWABLE (STORIES|AREA)|CONSTRUCTION TYPE:"),
    ("foundation_plan", r"FOUNDATION PLAN"),
    ("roof_framing_plan", r"ROOF FRAMING"),
    ("framing_plan", r"(LEVEL|FLOOR)?\s*(CEILING )?FRAMING PLAN"),
    ("column_schedule", r"COLUMN SCHEDULE"),
    ("pier_cap_schedule", r"PIER (CAP )?SCHEDULE"),
    ("roof_plan", r"ROOF PLAN"),
    ("floor_plan", r"FLOOR PLAN"),
    ("door_schedule", r"DOOR SCHEDULE"),
    ("window_schedule", r"WINDOW SCHEDULE"),
    ("finish_schedule", r"FINISH SCHEDULE"),
    ("exterior_finish_schedule", r"EXTERIOR FINISH SCHEDULE"),
    ("wall_type_schedule", r"WALL TYPE"),
    ("building_section", r"BUILDING SECTION"),
    ("exterior_elevation", r"EXTERIOR ELEVATION|BUILDING ELEVATION"),
    ("site_layout_plan", r"LAYOUT PLAN|OVERALL SITE PLAN"),
    ("grading_plan", r"GRADING PLAN"),
    ("drainage_plan", r"DRAINAGE (AREA MAP|PLAN)"),
    ("erosion_control_plan", r"EROSION CONTROL PLAN"),
    ("utility_plan", r"UTILITY PLAN"),
    ("landscape_plan", r"LANDSCAPE (NOTES|PLAN|DETAILS)"),
    ("general_notes", r"GENERAL (CONSTRUCTION )?NOTES"),
    ("mep_legend", r"FUSED DISCONNECT SWITCH|FLUORESCENT FIXTURE|MOTOR RATED SWITCH"),
]

COMPILED = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in SHEET_TYPE_PATTERNS]


def page_text(pdf_path: str, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True,
    )
    return result.stdout


def page_count(pdf_path: str) -> int:
    result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
    m = re.search(r"Pages:\s+(\d+)", result.stdout)
    return int(m.group(1)) if m else 0


def classify_page(text: str) -> list:
    flat = " ".join(text.split())
    return [name for name, pattern in COMPILED if pattern.search(flat)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Path to the discipline PDF")
    ap.add_argument("--discipline", default=None, help="Label to tag every page with, e.g. civil, structural, architectural")
    ap.add_argument("--out", default=None, help="Write manifest JSON here instead of stdout")
    args = ap.parse_args()

    n = page_count(args.pdf)
    if n == 0:
        print(f"FAIL: could not read page count from {args.pdf}")
        return

    manifest = {"file": args.pdf, "discipline": args.discipline, "page_count": n, "pages": []}
    unclassified = 0
    for pg in range(1, n + 1):
        text = page_text(args.pdf, pg)
        if not text.strip():
            manifest["pages"].append({"page": pg, "sheet_types": [], "note": "no extractable text (possible raster scan)"})
            unclassified += 1
            continue
        types = classify_page(text)
        # Sheet indexes (a page listing every sheet's title) are a near-
        # universal CD-set convention on page 1-2 of each discipline PDF,
        # and they falsely match many sheet types since they name them all.
        # Tested: a >=4-match threshold applied to EVERY page also
        # mislabels real content sheets whose own general notes cross-
        # reference other sheet types (e.g. a floor plan's notes mentioning
        # "refer to window schedule") — that's a false negative on a
        # high-value sheet, worse than under-flagging. So this rule is
        # deliberately restricted to the first 2 pages, where index pages
        # actually live. A content page with many matches elsewhere in the
        # document keeps its raw tags — that's a real signal ("this page
        # touches many topics, open and confirm") not a page to relabel away.
        if pg <= 2 and len(types) >= 4:
            manifest["pages"].append({
                "page": pg,
                "sheet_types": ["possible_sheet_index_or_toc"],
                "raw_matches": types,
            })
        elif types:
            manifest["pages"].append({"page": pg, "sheet_types": types})
        else:
            unclassified += 1

    manifest["unclassified_count"] = unclassified
    out = json.dumps(manifest, indent=2)
    if args.out:
        Path(args.out).write_text(out + "\n")
        print(f"Classified {len(manifest['pages'])}/{n} pages with a recognized sheet type "
              f"({unclassified} unclassified) -> {args.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
