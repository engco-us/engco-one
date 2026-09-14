#!/usr/bin/env python3
"""Print the required eval cases for an agent so a reviewer (human or the
orchestrating model) runs them consistently and logs a real pass/fail —
instead of re-deriving the eval scenarios from scratch every time.
Usage: python3 run_agent_eval.py --agent A-01
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "agent_registry.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True, help="Agent ID, e.g. A-01")
    args = ap.parse_args()

    data = json.loads(REGISTRY_PATH.read_text())
    agent = next((a for a in data["agents"] if a["id"] == args.agent), None)
    if agent is None:
        print(f"Unknown agent: {args.agent}")
        return

    eval_by_id = {e["id"]: e for e in data["eval_cases"]}
    print(f"Eval cases required before {args.agent} ({agent['name']}) moves to Pilot:\n")
    for eid in agent["required_evals"]:
        e = eval_by_id[eid]
        print(f"[{e['id']}] ({e['severity']}) {e['scenario']}")
        print(f"    Expected: {e['expected']}\n")
    print("Record prompt, sources, output, result, reviewer, and corrective action for each"
          " in the run log before changing status away from Draft.")


if __name__ == "__main__":
    main()
