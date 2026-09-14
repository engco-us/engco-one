# SOP-001 — Project Initiation & Numbering
Owner: Yusuf (Managing Partner) | Status: Draft | Priority: High

## Problem this fixes
Shehab 1 (BD) and Waqas (estimating) both touch incoming leads with no single owner — leads get worked twice, dropped, or never get a project ID until it's already messy.

## Rule
No project gets worked (design, estimate, field, invoice) until it has a project ID. One ID, assigned once, at first qualified contact — not at contract signing.

## Procedure
1. **Trigger**: any qualified lead (real scope, real client, real chance of proceeding) — from Shehab 1, Waqas, Mohammed, or anyone else.
2. **Whoever qualifies it runs**: `python3 scripts/new_project.py --name "..." --city ... --client "..." --type "..."`
   - Creates the `ENG-YYYY-###` ID, the 10-folder project tree, and the registry row (phase = Discovery, status = On Track, project_manager = TBD).
3. **Within 24 hours, Yusuf assigns the project_manager field** (update `data/project_registry.json` row) — this is the single named owner from that point forward. No project stays "TBD" past 24 hours.
4. **All further work on that project references the ID** — filenames, folders, invoices, field reports.

## Who owns what
- Qualifying a lead and running the script: whoever brought it in (Shehab 1, Waqas, Mohammed, etc.)
- Assigning project_manager: Yusuf only
- Keeping the registry row current: the assigned project_manager (`validate_record.py` flags it stale after 7 days)

## Exit criteria for this SOP
- 5 real leads run through this procedure with no ID collisions and no project worked before it had an ID.
