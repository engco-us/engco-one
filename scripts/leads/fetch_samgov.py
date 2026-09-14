#!/usr/bin/env python3
"""SAM.gov (federal) Opportunities connector — the documented, stable
public API (unlike ESBD's undocumented internal service).
https://open.gsa.gov/api/get-opportunities-public-api/

Requires a real SAM.gov public API key. Get one at sam.gov after creating
an account (Account Details page). NEVER commit the key — set it as an
environment variable:

  export SAM_GOV_API_KEY="your-real-key"

This connector has NOT been run against a real key yet (none was
available while building it) — the request shape below matches the
official documentation exactly, but treat it as unverified until it's
actually run once with a real key and the response checked.

Usage:
  export SAM_GOV_API_KEY=...
  python3 fetch_samgov.py --days-back 7 --state TX
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from lead_schema import Lead

ENDPOINT = "https://api.sam.gov/opportunities/v2/search"

# Construction/engineering-relevant NAICS codes, narrowing results instead
# of pulling every federal opportunity nationwide. Not exhaustive — add
# more as real leads show gaps.
DEFAULT_NAICS = [
    "237310",  # Highway, Street, and Bridge Construction
    "236220",  # Commercial and Institutional Building Construction
    "238910",  # Site Preparation Contractors
    "541330",  # Engineering Services
]

EXPECTED_KEYS = {"totalRecords", "limit", "offset", "opportunitiesData"}


class SchemaChanged(Exception):
    pass


def fetch_page(api_key: str, posted_from: str, posted_to: str, state: str,
               ncode: str, limit: int, offset: int) -> dict:
    params = {
        "api_key": api_key,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": limit,
        "offset": offset,
    }
    if state:
        params["state"] = state
    if ncode:
        params["ncode"] = ncode

    url = f"{ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "engco-one-leads-finder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read())

    if not EXPECTED_KEYS.issubset(payload.keys()):
        raise SchemaChanged(
            f"SAM.gov response shape changed — expected keys {EXPECTED_KEYS}, "
            f"got {set(payload.keys())}. Check https://open.gsa.gov/api/get-opportunities-public-api/ "
            "for the current schema before trusting this connector's output."
        )
    return payload


def to_lead(record: dict, now_iso: str) -> Lead:
    return Lead(
        source="SAM.gov",
        solicitation_id=record.get("solicitationNumber", record.get("noticeId", "")),
        title=record.get("title", ""),
        agency=record.get("fullParentPathName", record.get("department", "")),
        posted_date=record.get("postedDate"),
        due_date=record.get("responseDeadLine"),
        due_time=None,  # SAM.gov's responseDeadLine is a single datetime, not split
        status=record.get("type", ""),
        codes=record.get("naicsCode", ""),
        detail_url=record.get("uiLink", ""),
        attachment_links=[r.get("url", "") for r in record.get("resourceLinks", []) or []],
        first_seen=now_iso,
        last_checked=now_iso,
        source_evidence=record,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-back", type=int, default=7)
    ap.add_argument("--state", default="TX")
    ap.add_argument("--naics", default=None, help="Comma-separated NAICS codes; defaults to DEFAULT_NAICS")
    args = ap.parse_args()

    api_key = os.environ.get("SAM_GOV_API_KEY")
    if not api_key:
        print("FAIL: SAM_GOV_API_KEY environment variable not set. "
              "Get a free key at sam.gov (Account Details page) and export it — "
              "never pass it on the command line or commit it.", file=sys.stderr)
        sys.exit(1)

    today = datetime.now()
    posted_from = (today - timedelta(days=args.days_back)).strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")
    naics_codes = args.naics.split(",") if args.naics else DEFAULT_NAICS

    all_leads = []
    now_iso = datetime.now().isoformat(timespec="seconds")
    try:
        for ncode in naics_codes:
            offset = 0
            while True:
                payload = fetch_page(api_key, posted_from, posted_to, args.state, ncode, limit=100, offset=offset)
                records = payload["opportunitiesData"]
                all_leads.extend(to_lead(r, now_iso) for r in records)
                offset += 100
                if offset >= payload["totalRecords"] or not records:
                    break
    except SchemaChanged as e:
        print(f"SCHEMA_CHANGE_DETECTED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"FETCH_FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps([l.to_dict() for l in all_leads], indent=2))
    print(f"\n{len(all_leads)} SAM.gov leads fetched ({posted_from} to {posted_to}, "
          f"NAICS {naics_codes}).", file=sys.stderr)


if __name__ == "__main__":
    main()
