#!/usr/bin/env python3
"""Extract rows from an architectural interior door & frame schedule.

A door schedule table has one row per door: ID, location, width, height,
door/frame material+type+finish, fire rating, hardware group, remarks.
Confirmed real format (Nueces Mosque & Residential Tower, Arch p43):
most rows print as one clean pdftotext -layout line, but a schedule can
also pack two doors side by side as a small inset table, where each
field for both doors is printed as its OWN line, two values per line
(door N's value, then door N+1's value) — the same "strided" layout bug
already solved in extract_code_summary.py, applied to a new document.

A real permit set can carry more than one such schedule on the same
sheet — confirmed here: an INTERIOR DOOR & FRAME SCHEDULE (IDs like
102A, C103, ST103), a separate EXTERIOR DOOR & FRAME SCHEDULE (IDs like
X100, ST702), and a RESIDENT DOOR & FRAME SCHEDULE listing door TYPES
that repeat per unit (R1-R7, XR1), not one row per one of the 36 units.
One ID pattern covers all three because the row structure — ID, then
location, then two dimensions — is the same across all of them.

Refuses to guess a door ID: a token is only counted as one if it is
followed, in a parseable structure, by BOTH a location and two real
dimension tokens (WIDTH x HEIGHT). This matters — on this exact page, the
architect's own office address ("6010 Balcones Dr, Suite 200") contains
a bare "200" that looks exactly like a door ID and would be a false
positive without this guard, since numeric IDs on this page are
otherwise indistinguishable from a street suite number.

Two real bugs were caught and fixed by rendering this page as an image
and visually counting rows before trusting the first extraction pass
(54 doors) — it was wrong on two counts: (1) the location pattern didn't
allow a hyphen, so every "MULTI-PURPOSE" row silently failed to match
(6 real doors dropped with no error); (2) a legend label ("XF3") sitting
on the same text line as a real row, due to layout bleed, was swallowed
as if it were the door ID, mislabeling door "XR1". Fixed by widening the
ID pattern to cover the letter-prefixed schemes above, and by removing
digits from the location character class (no real location on this page
contains one, so a following ID token can no longer be mistaken for part
of the previous row's location). Re-verified against the rendered image:
92 real rows, text extraction now matches the visual count exactly.

Usage:
  python3 extract_door_schedule.py nueces_arch.pdf --page 43
  python3 extract_door_schedule.py nueces_arch.pdf --find-pages
"""
import argparse
import json
import re
import subprocess

DOOR_ID = r"[A-Z]{0,2}\d{1,3}[A-Z]?"
DIM = r"\d+'-\d+\""

# A real row: ID, then LOCATION (caps/apostrophes/&/./hyphen/spaces, no
# digits — no real location on this page contains one, which is what
# keeps a following door ID from being swallowed into this group), then
# two dimension tokens back to back (width, height). Requiring all four
# in sequence is what excludes stray numbers like a street suite number
# or a sheet/detail callout — those never have a location + two real
# dimensions immediately after them.
ROW_PATTERN = re.compile(
    rf"\b({DOOR_ID})\b\s+([A-Z][A-Z./&'\s-]{{1,40}}?)\s+({DIM})\s+({DIM})"
)

HEADER_WORDS = re.compile(r"\bSCHEDULE\b|\bDOOR PANEL TYPES\b|\bRE:\s*SCHEDULE\b")


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
    n = page_count(pdf_path)
    candidates = []
    for pg in range(1, n + 1):
        text = page_text(pdf_path, pg)
        if "DOOR" in text and "SCHEDULE" in text and len(re.findall(rf"\b{DOOR_ID}\b", text)) > 5:
            candidates.append(pg)
    return candidates


def _dims_to_sf(width: str, height: str) -> float:
    def feet_inches_to_ft(token: str) -> float:
        ft, inches = token.strip('"').split("'-")
        return int(ft) + int(inches) / 12
    return round(feet_inches_to_ft(width) * feet_inches_to_ft(height), 2)


def extract(pdf_path: str, page: int) -> dict:
    text = page_text(pdf_path, page)
    lines = [ln.strip() for ln in text.splitlines()]

    rows = []
    matched_ids = set()

    # Pass 1: single-line rows (id, location, width, height all on one line).
    for raw_line in lines:
        m = ROW_PATTERN.search(raw_line)
        if not m:
            continue
        door_id, location, width, height = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        rows.append({
            "door_id": door_id,
            "location": location,
            "width": width,
            "height": height,
            "area_sf": _dims_to_sf(width, height),
            "confidence": "schedule_verified",
            "source_line": raw_line,
        })
        matched_ids.add(door_id)

    # Pass 2: "strided" inset tables — a run of bare ID-only lines
    # immediately followed by N lines of paired field values (2 doors
    # per line). Only attempted when the stride can be inferred
    # unambiguously (a contiguous block of bare IDs, all unmatched by
    # pass 1); anything less regular is left unresolved, not guessed.
    bare_id_re = re.compile(rf"^({DOOR_ID})$")
    i = 0
    while i < len(lines):
        block_ids = []
        j = i
        while j < len(lines) and bare_id_re.match(lines[j]) and lines[j] not in matched_ids:
            block_ids.append(lines[j])
            j += 1
        if len(block_ids) >= 2:
            width_dim = re.compile(rf"^{DIM}$")
            # Next len(block_ids) lines after the ID block, in order, are:
            # location x N, width x N, height x N (each field type grouped).
            loc_lines = lines[j:j + len(block_ids)]
            width_lines = lines[j + len(block_ids):j + 2 * len(block_ids)]
            height_lines = lines[j + 2 * len(block_ids):j + 3 * len(block_ids)]
            ok = (
                len(loc_lines) == len(block_ids)
                and all(l and not width_dim.match(l) for l in loc_lines)
                and all(width_dim.match(l) for l in width_lines)
                and all(width_dim.match(l) for l in height_lines)
            )
            if ok:
                for k, door_id in enumerate(block_ids):
                    rows.append({
                        "door_id": door_id,
                        "location": loc_lines[k],
                        "width": width_lines[k],
                        "height": height_lines[k],
                        "area_sf": _dims_to_sf(width_lines[k], height_lines[k]),
                        "confidence": "schedule_verified",
                        "source_line": f"reconstructed from stride block at lines {i}-{j + 3 * len(block_ids)}",
                    })
                    matched_ids.add(door_id)
            i = j + 3 * len(block_ids) if ok else j + 1
        else:
            i += 1

    return {
        "source_file": pdf_path,
        "source_page": page,
        "door_count": len(rows),
        "total_door_area_sf": round(sum(r["area_sf"] for r in rows), 2),
        "rows": sorted(rows, key=lambda r: r["door_id"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, default=None)
    ap.add_argument("--find-pages", action="store_true")
    args = ap.parse_args()

    if args.find_pages:
        print(f"Candidate door schedule pages: {find_candidate_pages(args.pdf)}")
        return

    if args.page is None:
        print("FAIL: --page required (use --find-pages first to locate it)")
        return

    result = extract(args.pdf, args.page)
    print(json.dumps(result, indent=2))
    print(f"\nExtracted {result['door_count']} doors, {result['total_door_area_sf']} SF total, from page {args.page}.")


if __name__ == "__main__":
    main()
