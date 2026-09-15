# ENGCO ONE — local web app

A clean front door to the system — not a new source of truth. Every page
reads the real files in `data/*.json` directly; every button runs the real
script in `scripts/`, same as the `engco` CLI does. Nothing is duplicated
or cached.

## Run it
```
python3 webapp/app.py
```
Then open **http://127.0.0.1:5050**

## Pages
- **Dashboard** — agents/SOPs/projects at a glance, current scorecard, staleness flagged
- **Agents** — the real agent registry, status, owners, what each one owns, and the unassigned functions
- **SOPs** — the real 23-SOP backlog with status
- **Projects** — real registered projects + a form to register a new one (runs SOP-001)
- **Scorecard** — history + a form to log this week's numbers
- **Leads Finder** — run the real ESBD/Austin/SAM.gov connectors from a checkbox form, report-only (never submits a bid, never contacts an agency)

## Verified working (2026-09-14)
Tested in a real browser, not just written and assumed: every page renders
with live data, and the Leads Finder form was run end to end — pulled 113
real TxDOT leads and 584 real Austin permits through the actual UI.
