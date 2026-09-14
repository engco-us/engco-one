#!/usr/bin/env python3
"""ESBD (Electronic State Business Daily / Texas SmartBuy) connector.
Currently covers TxDOT only — confirmed the live agency list does NOT
contain the main City of Austin, City of Houston, or Harris County
entities (see docs/leads_finder_data_access_research.md). Do not extend
agency_number below to "cover" those three without re-confirming they've
appeared in the live agency list; assuming coverage that doesn't exist
was the mistake this research caught last time.

Uses the confirmed real but UNDOCUMENTED internal service
(ESBD.Service.ss) — verified live with a real request before this file
was written (111 real, current TxDOT records; response schema matched
what the research predicted exactly). This is not a stable contractual
API: the URL embeds a frontend package version. schema_ok() below checks
the response shape on every run and refuses to silently emit incomplete
records if the shape changes.

Usage:
  python3 fetch_esbd.py --days-back 7
  python3 fetch_esbd.py --start 09/01/2026 --end 09/14/2026
"""
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timedelta

from lead_schema import Lead

ENDPOINT = "https://www.txsmartbuy.gov/app/extensions/CPA/CPAMain/1.0.0/services/ESBD.Service.ss"
# The real filter field is "agency" holding the exact "Name - Number" string
# as shown in the live dropdown — NOT "agencyNumber" (a separate field that
# looks like it should work but is silently ignored server-side: verified
# by testing directly, sending agencyNumber alone returned 111-244 mixed-
# agency records with zero filtering applied). Confirmed via a live browser
# session with an XHR interceptor, reading the real <select name="agency">
# option value, not guessed from the API's field name alone.
TXDOT_AGENCY = "Texas Department of Transportation - 601"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

EXPECTED_TOP_KEYS = {"agencies", "lines", "page", "recordsPerPage", "totalRecordsFound"}
EXPECTED_LINE_KEYS = {
    "internalid", "title", "solicitationId", "responseDue", "responseTime",
    "agencyNumber", "agencyName", "status", "statusName", "postingDate",
    "nigpCodes", "url",
}


class SchemaChanged(Exception):
    pass


def schema_ok(payload: dict) -> bool:
    if not EXPECTED_TOP_KEYS.issubset(payload.keys()):
        return False
    lines = payload.get("lines", [])
    if lines and not EXPECTED_LINE_KEYS.issubset(lines[0].keys()):
        return False
    return True


def fetch_page(start_date: str, end_date: str, page: int) -> dict:
    body = json.dumps({
        "agency": TXDOT_AGENCY,
        "page": page,
        "dateRange": "custom",
        "startDate": start_date,
        "endDate": end_date,
        "urlRoot": "esbd",
        "isCSV": False,
    }).encode()

    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read())

    if not schema_ok(payload):
        raise SchemaChanged(
            "ESBD.Service.ss response shape changed — refusing to emit possibly-"
            "wrong records. Fall back to the public HTML search "
            "(https://www.txsmartbuy.gov/esbd) until this connector is updated. "
            "See docs/leads_finder_data_access_research.md for the schema this "
            "connector expects."
        )
    return payload


def fetch_all(start_date: str, end_date: str) -> list:
    records = []
    page = 1
    while True:
        payload = fetch_page(start_date, end_date, page)
        records.extend(payload["lines"])
        total = payload["totalRecordsFound"]
        per_page = payload["recordsPerPage"] or 24
        if page * per_page >= total or not payload["lines"]:
            break
        page += 1
    return records


def to_lead(record: dict, now_iso: str) -> Lead:
    return Lead(
        source="ESBD",
        solicitation_id=record["solicitationId"],
        title=record["title"],
        agency=record["agencyName"],
        posted_date=record.get("postingDate"),
        due_date=record.get("responseDue"),
        due_time=record.get("responseTime"),
        status=record.get("statusName", record.get("status", "")),
        codes=record.get("nigpCodes", ""),
        detail_url=record.get("url", ""),
        attachment_links=[],  # not present in this response shape; detail_url is the source of truth
        first_seen=now_iso,
        last_checked=now_iso,
        source_evidence=record,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-back", type=int, default=None, help="Rolling window: N days back from today")
    ap.add_argument("--start", default=None, help="MM/DD/YYYY (overrides --days-back)")
    ap.add_argument("--end", default=None, help="MM/DD/YYYY (defaults to today)")
    args = ap.parse_args()

    today = datetime.now()
    if args.start:
        start_date = args.start
        end_date = args.end or today.strftime("%m/%d/%Y")
    else:
        days_back = args.days_back or 7
        start_date = (today - timedelta(days=days_back)).strftime("%m/%d/%Y")
        end_date = today.strftime("%m/%d/%Y")

    try:
        records = fetch_all(start_date, end_date)
    except SchemaChanged as e:
        print(f"SCHEMA_CHANGE_DETECTED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"FETCH_FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    now_iso = datetime.now().isoformat(timespec="seconds")
    leads = [to_lead(r, now_iso) for r in records]
    print(json.dumps([l.to_dict() for l in leads], indent=2))
    print(f"\n{len(leads)} TxDOT leads fetched ({start_date} to {end_date}).", file=sys.stderr)


if __name__ == "__main__":
    main()
