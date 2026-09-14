#!/usr/bin/env python3
"""Surface corrections worth promoting into permanent agent instructions.
Doesn't auto-edit anything — promotion is a judgment call for the agent's
accountable owner. This just stops good corrections from getting lost in
the log and never acted on.
Usage:
  python3 promote_learning.py --list                # unpromoted corrections, grouped by agent
  python3 promote_learning.py --mark-promoted RUN-0003
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "agent_run_log.json"


def load():
    return json.loads(PATH.read_text())


def save(data):
    PATH.write_text(json.dumps(data, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--mark-promoted", default=None, help="Run ID, e.g. RUN-0003")
    args = ap.parse_args()

    data = load()

    if args.mark_promoted:
        run = next((r for r in data["runs"] if r["id"] == args.mark_promoted), None)
        if run is None:
            print(f"FAIL: {args.mark_promoted} not found")
            return
        run["promoted"] = True
        save(data)
        print(f"Marked {args.mark_promoted} as promoted — make sure the actual "
              f"edit landed in agents/{run['agent']}-*.md before treating this as done.")
        return

    unpromoted = [r for r in data["runs"] if r["correction"] and not r["promoted"]]
    if not unpromoted:
        print("No unpromoted corrections logged.")
        return

    by_agent = {}
    for r in unpromoted:
        by_agent.setdefault(r["agent"], []).append(r)

    for agent, runs in by_agent.items():
        flag = " <-- REPEATS, promote this" if len(runs) >= 2 else ""
        print(f"\n{agent} ({len(runs)} unpromoted correction(s)){flag}")
        for r in runs:
            print(f"  [{r['id']}] {r['task']}")
            print(f"    correction: {r['correction']}")


if __name__ == "__main__":
    main()
