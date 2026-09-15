#!/usr/bin/env python3
"""Extract the detention-basin summary table off a Harris County Flood
Control District "Review Sheet" — a standardized county form used on every
HCFCD-jurisdiction civil project, not a one-off.

Real, load-bearing difference from every other extractor in this toolkit:
this form's row/column LABELS are not in the PDF's extractable text layer
at all (they're baked into a raster background image — the fixed printed
form template), while the ENGINEER-FILLED VALUES are real vector text on
top of it. So this cannot be label-anchored regex like every other
extractor here. Instead it trusts the KNOWN, FIXED reading order of the
HCFCD PCPM Summary Table (confirmed against a real rendered project sheet,
9 rows x up-to-3 columns, in document order) — real numbers, positional
mapping, not vision, not guessed.

Because there is no label to anchor to, this is inherently more fragile
than the rest of this toolkit if Harris County revises the form layout.
Guarded two ways: (1) refuses to run unless the page's own real text
confirms it actually is this form ("HARRIS COUNTY", "FLOOD CONTROL
DISTRICT", "REVIEW SHEET" all present); (2) refuses to map values unless
exactly the expected count of 3-column rows is found — a layout change
would change that count and this correctly reports not_found instead of
silently mis-mapping shifted values.

Usage:
  python3 extract_hcfcd_detention.py plans.pdf --page N
  python3 extract_hcfcd_detention.py plans.pdf --find-pages
"""
import argparse
import json
import re
import subprocess

# Document order, confirmed against a real rendered HCFCD Review Sheet
# (6659 Satsuma Dr, Houston — HC Project 2607210179 / HCFCD 2607210184).
ROW_LABELS_3COL = [
    "Maximum allowable outflow (pre-development peak flow), cfs",
    "Maximum outflow provided (peak flow from basin), cfs",
    "Design water surface elevation, ft",
    "Minimum storage required, ac-ft",
    "Detention storage provided, ac-ft",
    "Storage rate provided, ac-ft/ac",
    "Outflow velocity into channel, ft/sec",
]
COLUMNS = ["50% exceedance (2-year)", "10% exceedance (10-year)", "1% exceedance (100-year)"]

TRIPLET = re.compile(r"(-?\d[\d,]*\.?\d*)\s{5,}(-?\d[\d,]*\.?\d*)\s{5,}(-?\d[\d,]*\.?\d*)(?:\s{2,}\D|\s*$)")
SIGNATURE_STRINGS = ["HARRIS COUNTY", "FLOOD CONTROL DISTRICT", "REVIEW SHEET"]


def page_text(pdf_path: str, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True,
    )
    return result.stdout


def page_count(pdf_path: str) -> int:
    result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
    m = re.search(r"Pages:\s+(\d+)", result.stdout)
    return int(m.group(1)) if m else 0


def is_hcfcd_review_sheet(text: str) -> bool:
    upper = text.upper()
    return all(s in upper for s in SIGNATURE_STRINGS)


def find_candidate_pages(pdf_path: str) -> list:
    n = page_count(pdf_path)
    return [pg for pg in range(1, n + 1) if is_hcfcd_review_sheet(page_text(pdf_path, pg))]


def extract(pdf_path: str, page: int) -> dict:
    text = page_text(pdf_path, page)
    result = {"source_file": pdf_path, "source_page": page, "is_hcfcd_review_sheet": is_hcfcd_review_sheet(text)}

    if not result["is_hcfcd_review_sheet"]:
        result["rows"] = []
        result["note"] = "Page does not carry the real 'HARRIS COUNTY / FLOOD CONTROL DISTRICT / REVIEW SHEET' text — refusing to apply the position-based schema to a page that isn't confirmed to be this form."
        return result

    triplet_lines = [m for m in (TRIPLET.search(line) for line in text.splitlines()) if m]

    if len(triplet_lines) != len(ROW_LABELS_3COL):
        result["rows"] = []
        result["note"] = (
            f"Found {len(triplet_lines)} three-column numeric rows, expected exactly {len(ROW_LABELS_3COL)} "
            "for this known form layout — refusing to map values to labels on a mismatched count rather "
            "than risk assigning a number to the wrong row."
        )
        return result

    rows = []
    for label, m in zip(ROW_LABELS_3COL, triplet_lines):
        values = [float(v.replace(",", "")) for v in m.groups()]
        rows.append({"row": label, "columns": dict(zip(COLUMNS, values))})
    result["rows"] = rows
    result["confidence"] = "schedule_verified"
    result["note"] = None
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, default=None)
    ap.add_argument("--find-pages", action="store_true")
    args = ap.parse_args()

    if args.find_pages:
        print(f"Candidate HCFCD Review Sheet pages: {find_candidate_pages(args.pdf)}")
        return

    if args.page is None:
        print("FAIL: --page required (use --find-pages first to locate it)")
        return

    result = extract(args.pdf, args.page)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
