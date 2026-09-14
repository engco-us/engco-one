#!/usr/bin/env python3
"""City of Austin building permits — the real, legitimate source for
PRIVATE (non-governmental) construction leads: private projects still
pull permits from the city, and permit records are public. Confirmed
live against the real Socrata Open Data API (data.austintexas.gov),
"Issued Construction Permits" dataset (3syk-w9eu).

A different, similarly-named "Commercial (New Construction) Building
Permits" dataset (d3mw-y7vr) was checked first and returned empty
records — looks stale/deprecated. Not used. Using the proven working
dataset instead, filtered to permit_class_mapped=Commercial.

No API key needed — Socrata's public datasets are open. A Socrata "app
token" is optional and only raises rate limits; not required to work.

Usage:
  python3 fetch_austin_permits.py --days-back 7
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from lead_schema import Lead

DATASET_URL = "https://data.austintexas.gov/resource/3syk-w9eu.json"

RELEVANT_WORK_CLASSES = {"New", "Addition", "Remodel"}  # excludes e.g. pure signage/demo-only if ever needed


def fetch(start_date: str, limit: int = 1000) -> list:
    where = f"permit_class_mapped='Commercial' AND issue_date >= '{start_date}'"
    params = {
        "$where": where,
        "$order": "issue_date DESC",
        "$limit": limit,
    }
    url = f"{DATASET_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "engco-one-leads-finder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if isinstance(data, dict) and "message" in data:
        raise RuntimeError(f"Austin permits API error: {data['message']}")
    return data


def to_lead(record: dict, now_iso: str) -> Lead:
    return Lead(
        source="Austin-Permits",
        solicitation_id=record.get("permit_number", record.get("project_id", "")),
        title=record.get("description", "")[:200] or record.get("permit_class", ""),
        agency=record.get("original_address1", ""),  # not a government agency; reuse field for the project address
        posted_date=record.get("applieddate"),
        due_date=None,  # permits don't have a "due date" the way bids do
        due_time=None,
        status=record.get("status_current", ""),
        codes=record.get("permit_class", ""),
        detail_url=(record.get("link") or {}).get("url", ""),
        attachment_links=[],
        first_seen=now_iso,
        last_checked=now_iso,
        source_evidence=record,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-back", type=int, default=7)
    args = ap.parse_args()

    start_date = (datetime.now() - timedelta(days=args.days_back)).strftime("%Y-%m-%dT00:00:00")
    records = fetch(start_date)
    now_iso = datetime.now().isoformat(timespec="seconds")
    leads = [to_lead(r, now_iso) for r in records]
    print(json.dumps([l.to_dict() for l in leads], indent=2))
    print(f"\n{len(leads)} Austin commercial permit leads fetched (since {start_date}).")


if __name__ == "__main__":
    main()
