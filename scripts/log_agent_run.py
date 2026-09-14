#!/usr/bin/env python3
"""Log one real agent run: what it was asked, what it produced, what the
human reviewer corrected. This is the raw material for improving an agent —
not a black box, a record someone can read back and act on.
Usage:
  python3 log_agent_run.py --agent A-05 --project ENG-2026-001 \
      --task "Draft daily field report from raw note" \
      --reviewer Shawqi --correction "Missed the rebar delivery delay" \
      --promote-to-instructions   # optional: flag it for promotion review
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "agent_run_log.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--project", default=None)
    ap.add_argument("--task", required=True)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--correction", default="", help="What the reviewer had to fix, if anything")
    ap.add_argument("--promote-to-instructions", action="store_true",
                     help="Flag this correction as a candidate to write permanently into the agent's .md file")
    args = ap.parse_args()

    data = json.loads(PATH.read_text())
    entry = {
        "id": f"RUN-{len(data['runs']) + 1:04d}",
        "agent": args.agent,
        "project": args.project,
        "task": args.task,
        "reviewer": args.reviewer,
        "correction": args.correction,
        "promotion_candidate": args.promote_to_instructions,
        "promoted": False,
        "logged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    data["runs"].append(entry)
    PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Logged {entry['id']} for {args.agent}.")
    if args.correction:
        print(f"Correction recorded: {args.correction}")
        print("If this same correction shows up again, promote it into "
              f"agents/{args.agent}-*.md so it stops recurring.")


if __name__ == "__main__":
    main()
