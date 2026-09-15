#!/usr/bin/env python3
"""Scaffold a new ENGCO project: folder tree + controls.json + registry row.
Usage: python3 new_project.py --name "Hidden Village" --city Tomball --client "Acme LLC" --type "Site Development"
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "projects"
REGISTRY_PATH = ROOT / "data" / "project_registry.json"

FOLDER_MAP = [
    "00 - Project Control", "01 - Contract and Scope", "02 - Site and Existing Conditions",
    "03 - Engineering", "04 - Permitting and Approvals", "05 - Preconstruction",
    "06 - Construction", "07 - Financial and Billing", "08 - Client Communications",
    "09 - Closeout and As-Builts",
]

REQUIRED_FIELDS = ["name", "city", "client", "type"]


def next_project_id(registry: dict) -> str:
    year = date.today().year
    existing = [p["project_id"] for p in registry["projects"] if p["project_id"].startswith(f"ENG-{year}-")]
    n = len(existing) + 1
    return f"ENG-{year}-{n:03d}"


def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--city", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--type", required=True)
    ap.add_argument("--phase", default="Discovery")
    ap.add_argument("--pm", default="")
    args = ap.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text())

    if args.phase not in registry["valid_phases"]:
        print(f"FAIL: invalid --phase {args.phase!r} (must be one of {registry['valid_phases']})")
        raise SystemExit(1)

    project_id = next_project_id(registry)
    folder_name = f"{project_id} | {args.name} | {args.city}"
    project_dir = PROJECTS_DIR / slugify(folder_name)

    for sub in FOLDER_MAP:
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    controls = {
        "project_id": project_id,
        "project_name": args.name,
        "city": args.city,
        "client": args.client,
        "project_type": args.type,
        "current_phase": args.phase,
        "overall_status": "On Track",
        "project_manager": args.pm,
        "start_date": date.today().isoformat(),
        "contacts": [],
        "milestones": [],
        "open_actions": [],
        "risks": [],
        "rfis": [],
        "submittals": [],
        "change_events": [],
    }
    (project_dir / "00 - Project Control" / "controls.json").write_text(json.dumps(controls, indent=2))

    registry["projects"].append({
        "project_id": project_id,
        "project_name": args.name,
        "city": args.city,
        "client": args.client,
        "project_type": args.type,
        "current_phase": args.phase,
        "overall_status": "On Track",
        "project_manager": args.pm,
        "contract_value": 0,
        "start_date": date.today().isoformat(),
        "forecast_finish": None,
        "last_update": date.today().isoformat(),
        "folder": str(project_dir.relative_to(ROOT)),
    })
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))

    print(f"Created {project_id} at {project_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
