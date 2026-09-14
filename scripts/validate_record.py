#!/usr/bin/env python3
"""Validate a project registry row (or controls.json) against required fields
and the phase/status vocab in data/project_registry.json. Never lets an agent
silently write a record with an invalid phase, missing owner, or stale update.
Usage: python3 validate_record.py --project-id ENG-2026-001
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "project_registry.json"

REQUIRED_ROW_FIELDS = [
    "project_id", "project_name", "city", "client", "project_type",
    "current_phase", "overall_status", "project_manager", "last_update",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", required=True)
    ap.add_argument("--max-staleness-days", type=int, default=7)
    args = ap.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text())
    row = next((p for p in registry["projects"] if p["project_id"] == args.project_id), None)
    if row is None:
        print(f"FAIL: {args.project_id} not found in registry")
        sys.exit(1)

    errors = []
    for field in REQUIRED_ROW_FIELDS:
        if not row.get(field):
            errors.append(f"missing required field: {field}")

    if row.get("current_phase") not in registry["valid_phases"]:
        errors.append(f"invalid phase: {row.get('current_phase')!r} (must be one of {registry['valid_phases']})")

    if row.get("overall_status") not in registry["valid_overall_status"]:
        errors.append(f"invalid status: {row.get('overall_status')!r} (must be one of {registry['valid_overall_status']})")

    last_update = row.get("last_update")
    if last_update:
        age = (date.today() - datetime.fromisoformat(last_update).date()).days
        if age > args.max_staleness_days:
            errors.append(f"last_update is {age} days old (max {args.max_staleness_days}) — stale status is not reliable status")

    if errors:
        print(f"FAIL: {args.project_id}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"PASS: {args.project_id}")


if __name__ == "__main__":
    main()
