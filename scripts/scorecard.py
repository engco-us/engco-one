#!/usr/bin/env python3
"""Weekly scorecard: log and check the 3 shared numbers (active_projects,
proposals_out, cash_position) so the weekly review has real data instead of
someone reconstructing it from memory.
Usage:
  python3 scorecard.py --add --week-of 2026-09-14 --active-projects 3 \
      --proposals-out 2 --cash-position 145000 --recorded-by Yusuf [--notes "..."]
  python3 scorecard.py --latest
  python3 scorecard.py --check --max-staleness-days 7
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "scorecard.json"


def load():
    return json.loads(PATH.read_text())


def save(data):
    PATH.write_text(json.dumps(data, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--week-of")
    ap.add_argument("--active-projects", type=int)
    ap.add_argument("--proposals-out", type=int)
    ap.add_argument("--cash-position", type=float)
    ap.add_argument("--recorded-by")
    ap.add_argument("--notes", default="")
    ap.add_argument("--max-staleness-days", type=int, default=7)
    args = ap.parse_args()

    data = load()

    if args.add:
        required = [args.week_of, args.active_projects, args.proposals_out,
                    args.cash_position, args.recorded_by]
        if any(v is None for v in required):
            print("FAIL: --add requires --week-of --active-projects --proposals-out "
                  "--cash-position --recorded-by")
            sys.exit(1)
        entry = {
            "week_of": args.week_of,
            "active_projects": args.active_projects,
            "proposals_out": args.proposals_out,
            "cash_position": args.cash_position,
            "recorded_by": args.recorded_by,
            "notes": args.notes,
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
        }
        # Replace any existing entry for the same week rather than piling up
        # duplicates — logging again for a week you already logged should
        # correct that entry, not create a second one.
        data["entries"] = [e for e in data["entries"] if e["week_of"] != args.week_of]
        data["entries"].append(entry)
        data["entries"].sort(key=lambda e: e["week_of"])
        save(data)
        print(f"Logged week_of {args.week_of}: {entry}")
        return

    if args.latest:
        if not data["entries"]:
            print("No entries yet.")
            return
        e = data["entries"][-1]
        print(json.dumps(e, indent=2))
        return

    if args.check:
        if not data["entries"]:
            print("FAIL: no scorecard entries ever recorded")
            sys.exit(1)
        last = data["entries"][-1]
        age = (date.today() - date.fromisoformat(last["week_of"])).days
        if age > args.max_staleness_days:
            print(f"FAIL: last entry is week_of {last['week_of']} ({age} days old, "
                  f"max {args.max_staleness_days}) — stale scorecard is not reliable status")
            sys.exit(1)
        print(f"PASS: current as of week_of {last['week_of']} ({age} days old)")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
