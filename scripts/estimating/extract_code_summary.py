#!/usr/bin/env python3
"""Pull known code-summary fields (gross SF, unit count, stories, per-floor
areas) off a general/cover sheet, with an exact citation for every value —
and cross-check the per-floor areas against the stated total, because two
numbers that should agree and don't is exactly the kind of thing a human
needs flagged, not silently trusted.

Uses `pdftotext -layout` (preserves column position) rather than plain
mode. Tested against a real set: plain mode interleaves multiple tables'
text unpredictably (a "FIRST FLOOR:" label appears in two different tables
on the same sheet — an allowable-area-ratio table with placeholder values,
and the real gross-SF table), which is unreliable to disambiguate. With
-layout, the real table's label is immediately followed by a bare number
token; the lookalike table's label is followed by "-", "UNLIMITED", or a
ratio expression — never a bare number. That's the filter this uses.

Refuses to guess: if a label exists but no valid value token follows it,
the field is reported not_found rather than filled with a nearby number.

Usage:
  python3 extract_code_summary.py "00 23015 GEN Permit.pdf" --page 2
"""
import argparse
import json
import re
import subprocess

NUMBER_TOKEN = re.compile(r"^[\d,]+$")

SIMPLE_FIELDS = [
    ("total_gross_building_sf", r"TOTAL BUILDING GROSS SF:", "sf"),
    ("total_unit_count", r"TOTAL UNIT COUNT:", "units"),
]

FLOOR_LABEL = re.compile(r"\b(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH) FLOOR:")
STORIES_LABEL = re.compile(r"TOTAL:\s*(\d+)\s*STORIES")


def page_text_layout(pdf_path: str, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True,
    )
    return result.stdout


def first_token_after(line: str, end_of_match: int):
    """Returns (token, token_start, token_end) for the first whitespace-
    delimited token after end_of_match, or (None, None, None)."""
    rest = line[end_of_match:]
    stripped = rest.lstrip()
    if not stripped:
        return None, None, None
    token = stripped.split()[0]
    token_start = end_of_match + (len(rest) - len(stripped))
    return token, token_start, token_start + len(token)


def snippet_around(line: str, start: int, end: int, radius: int = 60) -> str:
    # -layout mode pads huge runs of whitespace to preserve column
    # position, so a label far right on a wide sheet can sit past any fixed
    # truncation length. Window around the actual match instead of the
    # start of the line, and collapse the padding for readability.
    lo = max(0, start - radius)
    hi = min(len(line), end + radius)
    return re.sub(r"\s{2,}", "   ", line[lo:hi].strip())


def extract(text: str, page: int, pdf_path: str) -> dict:
    lines = text.splitlines()
    results = {"fields": [], "floor_areas": [], "cross_checks": []}

    for field_name, label_pat, unit in SIMPLE_FIELDS:
        found = False
        for line in lines:
            m = re.search(label_pat, line)
            if not m:
                continue
            token, tok_start, tok_end = first_token_after(line, m.end())
            if token and NUMBER_TOKEN.match(token):
                results["fields"].append({
                    "field": field_name, "value": token, "unit": unit,
                    "source_file": pdf_path, "source_page": page,
                    "source_snippet": snippet_around(line, m.start(), tok_end),
                    "confidence": "high",
                })
                found = True
                break
        if not found:
            results["fields"].append({"field": field_name, "value": None, "unit": unit,
                                       "source_file": pdf_path, "source_page": page,
                                       "confidence": "not_found"})

    stories_found = False
    for line in lines:
        m = STORIES_LABEL.search(line)
        if m:
            results["fields"].append({
                "field": "total_stories", "value": m.group(1), "unit": "stories",
                "source_file": pdf_path, "source_page": page,
                "source_snippet": snippet_around(line, m.start(), m.end()), "confidence": "high",
            })
            stories_found = True
            break
    if not stories_found:
        results["fields"].append({"field": "total_stories", "value": None, "unit": "stories",
                                   "source_file": pdf_path, "source_page": page, "confidence": "not_found"})

    # Per-floor areas: only accept a floor label whose immediate next token
    # is a bare number. Rejects the lookalike allowable-area-ratio table,
    # which always has "-", "UNLIMITED", or a ratio expression there instead.
    for line in lines:
        m = FLOOR_LABEL.search(line)
        if not m:
            continue
        token, tok_start, tok_end = first_token_after(line, m.end())
        if token and NUMBER_TOKEN.match(token):
            results["floor_areas"].append({
                "field": f"{m.group(1).lower()}_floor_area", "value": token, "unit": "sf",
                "source_file": pdf_path, "source_page": page,
                "source_snippet": snippet_around(line, m.start(), tok_end), "confidence": "high",
            })

    total_field = next((f for f in results["fields"] if f["field"] == "total_gross_building_sf"), None)
    if results["floor_areas"] and total_field and total_field["value"]:
        summed = sum(int(f["value"].replace(",", "")) for f in results["floor_areas"])
        stated = int(total_field["value"].replace(",", ""))
        results["cross_checks"].append({
            "check": "sum(per-floor gross SF) == stated total gross SF",
            "summed_value": summed,
            "stated_value": stated,
            "match": summed == stated,
            "delta": summed - stated,
        })

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, required=True, help="Page number of the code summary sheet (use classify_sheets.py to find it)")
    args = ap.parse_args()

    text = page_text_layout(args.pdf, args.page)
    results = extract(text, args.page, args.pdf)
    print(json.dumps(results, indent=2))

    not_found = [f["field"] for f in results["fields"] if f["confidence"] == "not_found"]
    if not_found:
        print(f"\nNOT FOUND (reported honestly, not guessed): {not_found}")
    for c in results["cross_checks"]:
        status = "PASS" if c["match"] else "MISMATCH - FLAG FOR REVIEW"
        print(f"\nCROSS-CHECK [{status}]: {c['check']} -> summed={c['summed_value']}, stated={c['stated_value']}, delta={c['delta']}")


if __name__ == "__main__":
    main()
