#!/usr/bin/env python3
"""Report-only leads aggregator. Runs each connector, dedupes by
source+solicitation_id, tracks first_seen across runs, and writes a
report. Never submits bids, never contacts an agency, never does
anything but read and report — per the explicit build instruction.

Persists state in data/leads/seen_leads.json so first_seen survives
across daily runs (a lead seen yesterday keeps yesterday's first_seen
today, even though last_checked updates every run).

Usage:
  python3 run_leads_report.py --days-back 7           # ESBD/TxDOT only (no key needed)
  python3 run_leads_report.py --days-back 7 --samgov   # also run SAM.gov (needs SAM_GOV_API_KEY)
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STATE_PATH = ROOT / "data" / "leads" / "seen_leads.json"
CONSTRUCTION_KEYWORDS = [
    "construction", "engineering", "paving", "drainage", "roadway", "bridge",
    "utility", "utilities", "site work", "grading", "permit", "surveying",
    "civil", "concrete", "asphalt", "trail", "culvert", "sidewalk",
]


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def run_connector(script: str, args: list) -> tuple:
    result = subprocess.run(
        ["python3", str(Path(__file__).parent / script)] + args,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return [], result.stderr.strip()
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError:
        return [], f"{script} produced unparseable output"


def is_relevant(lead: dict) -> bool:
    haystack = f"{lead['title']} {lead['codes']}".lower()
    return any(kw in haystack for kw in CONSTRUCTION_KEYWORDS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-back", type=int, default=7)
    ap.add_argument("--samgov", action="store_true", help="Also run the SAM.gov connector (needs SAM_GOV_API_KEY)")
    args = ap.parse_args()

    state = load_state()
    now_iso = datetime.now().isoformat(timespec="seconds")
    errors = []
    all_leads = []

    esbd_leads, err = run_connector("fetch_esbd.py", ["--days-back", str(args.days_back)])
    all_leads.extend(esbd_leads)
    if err:
        errors.append(f"ESBD: {err}")

    if args.samgov:
        sam_leads, err = run_connector("fetch_samgov.py", ["--days-back", str(args.days_back)])
        all_leads.extend(sam_leads)
        if err:
            errors.append(f"SAM.gov: {err}")

    new_count = 0
    updated_leads = []
    for lead in all_leads:
        key = f"{lead['source']}:{lead['solicitation_id']}"
        if key in state:
            lead["first_seen"] = state[key]["first_seen"]
        else:
            new_count += 1
        lead["last_checked"] = now_iso
        state[key] = lead
        updated_leads.append(lead)

    save_state(state)

    relevant = [l for l in updated_leads if is_relevant(l)]

    print(f"=== Leads Report — {now_iso} ===")
    print(f"Total leads fetched this run: {len(updated_leads)} ({new_count} new)")
    print(f"Flagged as construction/engineering-relevant: {len(relevant)}")
    if errors:
        print(f"\nERRORS (report-only, nothing else affected):")
        for e in errors:
            print(f"  - {e}")

    print(f"\n--- Relevant leads ---")
    for l in sorted(relevant, key=lambda x: x.get("due_date") or ""):
        marker = "[NEW]" if state[f"{l['source']}:{l['solicitation_id']}"]["first_seen"] == now_iso else ""
        print(f"{marker} [{l['source']}] {l['title']}")
        print(f"    Agency: {l['agency']} | Due: {l['due_date']} {l['due_time'] or ''} | Status: {l['status']}")
        print(f"    {l['detail_url']}")

    print(f"\nReport-only mode: no bids submitted, no agencies contacted, no external messages sent.")


if __name__ == "__main__":
    main()
