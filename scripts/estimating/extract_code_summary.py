#!/usr/bin/env python3
"""Pull known code-summary fields (gross SF, unit count, stories, etc.) off
a general/cover sheet, with an exact citation for every value.

Real CD-set code-summary tables are typeset in complex multi-column layouts,
so a label and its value are almost never on the same extracted text line —
tested against a real set, the value consistently lands 2 lines after its
label (label, blank line, value). This handles that, and REFUSES to guess:
if a label exists but no numeric value is found nearby, the field is
reported as not_found rather than skipped silently or filled with a nearby
unrelated number.

Usage:
  python3 extract_code_summary.py "00 23015 GEN Permit.pdf" --page 2
"""
import argparse
import json
import re
import subprocess

# (field_name, label_pattern, value_pattern, unit, mode)
# mode "inline": value is captured directly from the same regex as the label.
# mode "forward": find the label line, then scan the next few lines for the
# first one that looks like this value's shape.
FIELDS = [
    ("total_gross_building_sf", r"TOTAL BUILDING GROSS SF:?", r"^[\d,]+$", "sf", "forward"),
    ("total_unit_count", r"TOTAL UNIT COUNT:?", r"^\d+$", "units", "forward"),
    ("total_stories", r"TOTAL:\s*(\d+)\s*STORIES", None, "stories", "inline"),
]


def page_lines(pdf_path: str, page: int) -> list:
    result = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True,
    )
    return result.stdout.splitlines()


def extract(lines: list, page: int, pdf_path: str) -> list:
    results = []
    for field_name, label_pat, value_pat, unit, mode in FIELDS:
        if mode == "inline":
            found = False
            for i, line in enumerate(lines):
                m = re.search(label_pat, line)
                if m:
                    results.append({
                        "field": field_name,
                        "value": m.group(1),
                        "unit": unit,
                        "source_file": pdf_path,
                        "source_page": page,
                        "source_snippet": line.strip(),
                        "confidence": "high",
                    })
                    found = True
                    break
            if not found:
                results.append({"field": field_name, "value": None, "unit": unit,
                                 "source_file": pdf_path, "source_page": page,
                                 "confidence": "not_found"})
            continue

        # forward mode
        found = False
        for i, line in enumerate(lines):
            if re.search(label_pat, line):
                for j in range(i + 1, min(i + 5, len(lines))):
                    candidate = lines[j].strip()
                    if candidate and re.match(value_pat, candidate):
                        results.append({
                            "field": field_name,
                            "value": candidate,
                            "unit": unit,
                            "source_file": pdf_path,
                            "source_page": page,
                            "source_snippet": f"{line.strip()!r} -> {candidate!r} ({j - i} lines below)",
                            "confidence": "high",
                        })
                        found = True
                        break
                if found:
                    break
        if not found:
            results.append({"field": field_name, "value": None, "unit": unit,
                             "source_file": pdf_path, "source_page": page,
                             "confidence": "not_found"})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, required=True, help="Page number of the code summary sheet (use classify_sheets.py to find it)")
    args = ap.parse_args()

    lines = page_lines(args.pdf, args.page)
    results = extract(lines, args.page, args.pdf)
    print(json.dumps(results, indent=2))
    not_found = [r["field"] for r in results if r["confidence"] == "not_found"]
    if not_found:
        print(f"\nNOT FOUND (reported honestly, not guessed): {not_found}")


if __name__ == "__main__":
    main()
