#!/usr/bin/env python3
"""Extract line items from a TxDOT Estimate & Quantity (E&Q) Sheet — a
standardized statewide bid-item table, present on every TxDOT letting plan
set. Bid codes (e.g. "500-7001") are standardized statewide, so this can
eventually cross-reference real TxDOT Average Low Bid Unit Price data for
actual pricing, not just quantities.

Refuses to guess: only emits a row when bid code, unit, and quantity all
parse cleanly from one line; anything else is skipped, not guessed at.

Usage:
  python3 extract_txdot_eq.py martin.pdf --page 10
  python3 extract_txdot_eq.py martin.pdf --find-pages   # locate likely E&Q pages first
"""
import argparse
import json
import re
import subprocess

# Two real formats confirmed on independently downloaded TxDOT plan sets:
#   "Estimate & Quantity Sheet": 3-digit bid code, EST + FINAL columns
#     e.g. "105-7028   RMV (8") TRT/UNTRT BASE & ASPH PAV   SY   115,534.000   115,534.000"
#   "Quantity Summary" (seen on a different real project, smaller maintenance
#     contract style): 4-digit bid code, single QTY column, no decimals
#     e.g. "0350-7001   MICROSURFACING   TON   381"
# The final quantity group is optional to cover both.
ROW_PATTERN = re.compile(
    r"^\s*(\d{3,4}-\d{4})\s+(.+?)\s{2,}([A-Z]{1,4})\s+([\d,]+(?:\.\d+)?)(?:\s+([\d,]+(?:\.\d+)?))?\s*$"
)

UNIT_TOKENS = re.compile(r"\b(SY|CY|LF|TON|EA|STA|MO|LS|HR|SF|GAL|LB|DAY)\b")


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


def find_candidate_pages(pdf_path: str) -> list:
    """Cheap pre-scan: a real E&Q table page has many unit-abbreviation
    hits close together. Sheet-index page numbers don't reliably map to
    PDF page numbers in these documents (confirmed on a real 74-page
    TxDOT set, where the printed 'Sheet 6' E&Q table was actually on PDF
    page 10) — so this scans content, not the index."""
    n = page_count(pdf_path)
    candidates = []
    for pg in range(1, n + 1):
        text = page_text(pdf_path, pg)
        # Threshold tested down from >15: a real "Quantity Summary" sheet
        # (a second confirmed real TxDOT format, smaller maintenance-
        # contract style, one CSJ per page) had only 13 hits and was
        # missed entirely at the higher threshold. Lowering this is safe
        # since the strict row parser (not this heuristic) is what
        # actually prevents garbage — tested to correctly return zero
        # rows on non-matching pages even when flagged as a candidate.
        if len(UNIT_TOKENS.findall(text)) > 8:
            candidates.append(pg)
    return candidates


def extract(pdf_path: str, page: int) -> list:
    text = page_text(pdf_path, page)
    rows = []
    for line in text.splitlines():
        m = ROW_PATTERN.match(line)
        if not m:
            continue
        est = float(m.group(4).replace(",", ""))
        final = float(m.group(5).replace(",", "")) if m.group(5) else None
        rows.append({
            "bid_code": m.group(1),
            "description": m.group(2).strip(),
            "unit": m.group(3),
            "est_quantity": est,
            "final_quantity": final,  # None on single-column "Quantity Summary" sheets
            "source_file": pdf_path,
            "source_page": page,
            "source_line": line.strip(),
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, default=None)
    ap.add_argument("--find-pages", action="store_true")
    args = ap.parse_args()

    if args.find_pages:
        pages = find_candidate_pages(args.pdf)
        print(f"Candidate E&Q pages: {pages}")
        return

    if args.page is None:
        print("FAIL: --page required (use --find-pages first to locate it)")
        return

    rows = extract(args.pdf, args.page)
    print(json.dumps(rows, indent=2))
    print(f"\nExtracted {len(rows)} bid items from page {args.page}.")


if __name__ == "__main__":
    main()
