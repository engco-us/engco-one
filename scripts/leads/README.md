# Leads Finder

Report-only. Monitors public bid/RFP sources and flags construction/
engineering-relevant opportunities. **Never submits bids, never contacts
an agency, never sends anything anywhere** — it reads and reports, that's
the whole scope of this phase (per the build instructions this was
scoped from).

## Tools
- `lead_schema.py` — the one common `Lead` record every connector produces, regardless of source.
- `fetch_esbd.py` — TxDOT lettings via ESBD (Electronic State Business Daily / Texas SmartBuy). No API key needed. **Verified working with real, current data.**
- `fetch_samgov.py` — federal opportunities via SAM.gov's documented public API. Needs `SAM_GOV_API_KEY` (get one free at sam.gov, Account Details page — never commit it). **Not yet run against a real key; request shape matches official docs but is unverified until it's actually tested.**
- `run_leads_report.py` — runs the connectors, dedupes by `source:solicitation_id`, tracks `first_seen` across runs in `data/leads/seen_leads.json` (gitignored — runtime state, not source data), flags construction/engineering-relevant leads by keyword, prints a report.

## Coverage — what this does NOT cover yet, on purpose
City of Austin, City of Houston, and Harris County are **not** covered.
Confirmed directly: their main procurement entities do not appear in
ESBD's live agency list (only related-but-distinct entities like transit
authorities or appraisal districts do). Treating ESBD as a stand-in for
these three would silently miss real local opportunities — they need
separate integrations, researched independently. See
`docs/leads_finder_data_access_research.md`.

## A real bug found and fixed while building this (2026-09-14)
The research doc's confirmed request example used `"agencyNumber": "601"`
to filter to TxDOT. Testing it directly returned **111-244 mixed-agency
records with zero filtering applied** — `agencyNumber` is a real field in
the DOM but is silently ignored server-side. Found the actual working
filter by installing an XHR interceptor in a live browser session and
reading the real `<select name="agency">` field's value: the correct
parameter is `"agency"` holding the **full display string**
(`"Texas Department of Transportation - 601"`), not just the number.
Verified after the fix: 122/122 returned records were genuinely TxDOT
(`agencyNumber: "601"` on every one), across two full runs confirming
dedup also works correctly (second run: 0 new out of 122).

## Usage
```
python3 run_leads_report.py --days-back 7              # ESBD/TxDOT only, no key needed
export SAM_GOV_API_KEY=...
python3 run_leads_report.py --days-back 7 --samgov      # + SAM.gov
```

## Stability note
ESBD's `ESBD.Service.ss` endpoint is real and directly callable but is
**not a documented, contractual API** — its URL embeds a frontend package
version (`CPA/CPAMain/1.0.0`) that Texas SmartBuy can change without
notice. `fetch_esbd.py` checks the response shape on every run
(`schema_ok()`) and refuses to emit records if it changes, rather than
silently producing wrong data. The documented HTML-search fallback
(`https://www.txsmartbuy.gov/esbd`) is not yet built — known gap, not
hidden: a schema-change failure currently means "wait for a fix," not an
automatic fallback.
