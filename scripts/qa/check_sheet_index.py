#!/usr/bin/env python3
"""Catch a plan set that's missing a sheet, has one out of order, or has a
sheet mislabeled — a real, boring, expensive mistake that currently only
gets caught by a human flipping through every page by hand.

Method: a cover sheet's own printed "SHEET INDEX" is the source of truth
for what SHOULD be in the set (sheet number + title, read as real text,
never guessed). Independently, almost every drafting title block prints
a small self-identifying "current sheet / total sheets" number pair in
its corner (e.g. a page reading "04" and "08" side by side means "this is
sheet 4 of 8") — confirmed as real, consistently extractable text across
a real 8-page City of Houston water-line plan set (D+A Associates). This
script cross-checks the two: does the PDF's real page count match the
index's sheet count, and does each interior page's own stamped position
match where it actually sits in the file?

The cover sheet is a known, real exception: its own template usually
carries the sheet index instead of a numeric self-ID stamp, so it's
identified by definition (it's the page the index itself came from) and
noted as skipped, not treated as a false gap.

Refuses to guess: if the index can't be parsed, or a page's stamp can't
be found, that page is reported as unconfirmed — never assumed correct
and never assumed wrong.

Usage:
  python3 check_sheet_index.py plan_set.pdf
"""
import argparse
import json
import re
import subprocess

INDEX_ROW = re.compile(r"\b(\d{2})\s{2,}([A-Z][A-Z0-9 /'.\-]{2,60}?)(?:\s{2,}|$)")
STAMP_PAIR = re.compile(r"\b(\d{2})[ \t]{4,}(\d{2})\b")


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


def find_sheet_index(pdf_path: str, cover_page: int = 1):
    """Look for a real 'SHEET INDEX' block on the cover page and parse its
    rows. Returns (index_page, [(sheet_no, title), ...]) or (None, [])."""
    text = page_text(pdf_path, cover_page)
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if "SHEET INDEX" in l.upper()), None)
    if start is None:
        return None, []
    rows = []
    # Scan a generous window after the heading rather than stopping at the
    # first non-matching line: a real index row can share a text line with
    # unrelated content (e.g. a caption from a location-map graphic sitting
    # at the same vertical position) due to how -layout mode merges columns
    # — the same layout-bleed issue this toolkit has hit before. Only keep
    # rows that continue the expected 01, 02, 03... sequence, which is what
    # actually filters out any unrelated stray match.
    next_expected = 1
    for line in lines[start + 1:start + 40]:
        m = INDEX_ROW.search(line)
        if not m:
            continue
        sheet_no, title = m.group(1), m.group(2).strip()
        if int(sheet_no) != next_expected:
            continue
        if not title or len(title) < 3:
            continue
        rows.append((sheet_no, title))
        next_expected += 1
    return cover_page, rows


def find_stamp(text: str):
    """Return (current, total) as ints from the first plausible self-ID
    stamp pair found on the page, or None if no candidate exists."""
    for m in STAMP_PAIR.finditer(text):
        cur, tot = int(m.group(1)), int(m.group(2))
        if 1 <= cur <= 99 and 1 <= tot <= 99 and cur <= tot:
            return cur, tot
    return None


def check(pdf_path: str) -> dict:
    n_pages = page_count(pdf_path)
    index_page, index_rows = find_sheet_index(pdf_path)

    result = {
        "file": pdf_path,
        "pdf_page_count": n_pages,
        "sheet_index_found_on_page": index_page,
        "sheet_index_count": len(index_rows),
        "sheet_index": [{"sheet_no": no, "title": title} for no, title in index_rows],
        "issues": [],
        "page_checks": [],
    }

    if index_page is None:
        result["issues"].append("No 'SHEET INDEX' block found on the cover page — cannot cross-check, not assumed fine.")
        return result

    if len(index_rows) != n_pages:
        result["issues"].append(
            f"Sheet index lists {len(index_rows)} sheets but the PDF has {n_pages} pages — "
            "mismatch is real and unresolved, not reconciled by guessing which is right."
        )

    for pg in range(1, n_pages + 1):
        if pg == index_page:
            result["page_checks"].append({
                "page": pg, "status": "skipped_cover_sheet",
                "note": "Cover sheet carries the index itself; no numeric self-ID stamp expected on this template.",
            })
            continue

        text = page_text(pdf_path, pg)
        stamp = find_stamp(text)
        if stamp is None:
            result["page_checks"].append({"page": pg, "status": "unconfirmed", "note": "No self-ID stamp pattern found on this page."})
            result["issues"].append(f"Page {pg}: no self-identifying sheet-number stamp found — unconfirmed, not assumed correct.")
            continue

        cur, tot = stamp
        ok = (cur == pg) and (tot == n_pages)
        result["page_checks"].append({
            "page": pg, "status": "match" if ok else "MISMATCH",
            "stamped_as": f"{cur} of {tot}", "expected": f"{pg} of {n_pages}",
        })
        if not ok:
            result["issues"].append(f"Page {pg}: stamped as sheet {cur} of {tot}, but sits at PDF page {pg} of {n_pages} — real mismatch.")

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    args = ap.parse_args()
    result = check(args.pdf)
    print(json.dumps(result, indent=2))
    if result["issues"]:
        print(f"\n{len(result['issues'])} issue(s) found — see above.")
    else:
        print(f"\nClean: {result['pdf_page_count']} pages, all self-identified correctly against the sheet index.")


if __name__ == "__main__":
    main()
