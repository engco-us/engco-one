#!/usr/bin/env python3
"""Derive the two scorecard numbers that don't actually need a human to
retype them every week — they're already sitting, correctly, in the real
project registry.

active_projects = every row currently in data/project_registry.json.
proposals_out = every project whose current_phase is "Preconstruction" —
  not an invented rule: data/project_registry.json's own phase_gates table
  defines Preconstruction as the pricing stage (gate in: "pricing
  assumptions documented"; gate out to Construction: "authorization"),
  i.e. the stage where a project has a price out the door awaiting award.

cash_position is NOT derived here — there is no real accounting/bank data
source connected to this system, so guessing at that number would be
exactly the kind of invented figure this whole toolkit refuses to produce.
It stays a real, flagged, human-entered value until a real source exists.

Usage:
  python3 scorecard_auto.py                    # just show the derived numbers
  python3 scorecard_auto.py --add --cash-position N --recorded-by NAME [--week-of YYYY-MM-DD]
"""
import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "project_registry.json"


def derive():
    registry = json.loads(REGISTRY_PATH.read_text())
    projects = registry["projects"]
    active_projects = len(projects)
    proposals_out = [p for p in projects if p["current_phase"] == "Preconstruction"]
    return {
        "active_projects": active_projects,
        "proposals_out": len(proposals_out),
        "proposals_out_detail": [p["project_id"] + " — " + p["project_name"] for p in proposals_out],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", action="store_true", help="Log a scorecard entry using the derived numbers")
    ap.add_argument("--cash-position", type=float, help="Still manual — no real accounting source connected")
    ap.add_argument("--recorded-by")
    ap.add_argument("--week-of", default=date.today().isoformat())
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    derived = derive()
    print(json.dumps(derived, indent=2))

    if not args.add:
        return

    if args.cash_position is None or not args.recorded_by:
        print("\nFAIL: --add requires --cash-position and --recorded-by (cash position has no real source to derive from yet)")
        sys.exit(1)

    cmd = [
        "python3", str(ROOT / "scripts" / "scorecard.py"), "--add",
        "--week-of", args.week_of,
        "--active-projects", str(derived["active_projects"]),
        "--proposals-out", str(derived["proposals_out"]),
        "--cash-position", str(args.cash_position),
        "--recorded-by", args.recorded_by,
        "--notes", args.notes or f"active_projects/proposals_out auto-derived from project_registry.json; proposals: {', '.join(derived['proposals_out_detail']) or 'none'}",
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
