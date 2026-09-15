#!/usr/bin/env python3
"""Try every real, proven quantity extractor against a PDF and report only
the ones that actually matched something real.

This exists because sheet classification alone (classify_sheets.py) is
NOT a quantity takeoff — it tags what's on each page, it never produces a
number. Confusing the two is a real mistake this toolkit made once already
(shipped a "Quantity takeoff" UI that only ran classification and showed
the user a page-tag list with no quantities on it). This script is the
honest fix: run every extractor this toolkit actually has proof it works
(COMcheck, REScheck, TxDOT E&Q, door schedules, HCFCD detention review
sheets), and say plainly when none of them match, rather than silently
showing something that looks like an answer but isn't one.

This is NOT a general "extract quantities from any construction PDF"
tool — no such thing exists, and pretending otherwise would repeat the
same mistake. A document type with no extractor here (e.g. a civil
water-line plan-and-profile set, like ENG-2026-002/Kingwood) genuinely
needs bespoke engineering, the same way Kingwood's pipe lengths needed
real station-math work this session, not a button.

Usage:
  python3 auto_extract.py plans.pdf
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import extract_comcheck
import extract_rescheck
import extract_txdot_eq
import extract_door_schedule
import extract_hcfcd_detention


def try_comcheck(pdf_path: str):
    text = extract_comcheck.get_text(pdf_path)
    result = extract_comcheck.extract(text, pdf_path)
    if result.get("floor_area_sf") is not None:
        return {"extractor": "comcheck", "result": result}
    return None


def try_rescheck(pdf_path: str):
    text = extract_rescheck.get_text(pdf_path)
    result = extract_rescheck.extract(text, pdf_path)
    if result.get("conditioned_floor_area_sf") is not None:
        return {"extractor": "rescheck", "result": result}
    return None


def try_txdot(pdf_path: str):
    pages = extract_txdot_eq.find_candidate_pages(pdf_path)
    all_rows = []
    for pg in pages:
        rows = extract_txdot_eq.extract(pdf_path, pg)
        all_rows.extend(rows)
    if all_rows:
        return {"extractor": "txdot_eq", "pages_checked": pages, "rows": all_rows}
    return None


def try_door_schedule(pdf_path: str):
    pages = extract_door_schedule.find_candidate_pages(pdf_path)
    matches = []
    for pg in pages:
        result = extract_door_schedule.extract(pdf_path, pg)
        if result["door_count"] > 0:
            matches.append(result)
    if matches:
        return {"extractor": "door_schedule", "pages": matches}
    return None


def try_hcfcd_detention(pdf_path: str):
    pages = extract_hcfcd_detention.find_candidate_pages(pdf_path)
    matches = []
    for pg in pages:
        result = extract_hcfcd_detention.extract(pdf_path, pg)
        if result.get("rows"):
            matches.append(result)
    if matches:
        return {"extractor": "hcfcd_detention", "pages": matches}
    return None


def run(pdf_path: str) -> dict:
    matched = []
    for tryer in (try_comcheck, try_rescheck, try_txdot, try_door_schedule, try_hcfcd_detention):
        hit = tryer(pdf_path)
        if hit:
            matched.append(hit)
    return {
        "pdf": pdf_path,
        "matched_count": len(matched),
        "matched": matched,
        "note": (
            "No known quantity extractor matched this document — this is honest, not a bug. "
            "This toolkit only auto-extracts document types it has real proof on (COMcheck, "
            "REScheck, TxDOT E&Q sheets, door schedules). A new document type needs real "
            "engineering work before it can run through here, the same way Kingwood's pipe "
            "lengths and Nueces's door schedule did."
        ) if not matched else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    args = ap.parse_args()
    print(json.dumps(run(args.pdf), indent=2))


if __name__ == "__main__":
    main()
