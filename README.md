# ENGCO ONE

The operating system for ENGCO's integrated engineering, permitting, and construction delivery — one shared project record, seven specialized AI agents, human approval on everything that leaves the building.

## Structure
- `docs/` — company-wide agent instructions + the Active Project Operating Guide (how a project actually moves through the company)
- `agents/` — one deployment package per specialized agent (A-01 through A-07), each inheriting `docs/company_wide_instructions.md` plus its own mission, boundaries, and required evals
- `data/` — machine-readable registries: `agent_registry.json` (agents + eval cases), `sop_backlog.json` (22 procedures still to write, prioritized), `project_registry.json` (the live portfolio + phase-gate rules)
- `scripts/` — automation so agents don't reason through mechanical work from scratch every run:
  - `new_project.py` — scaffolds a project's folder tree + registry entry
  - `validate_record.py` — checks a project record against required fields/vocab before it's trusted
  - `run_agent_eval.py` — prints an agent's required eval cases for consistent testing
  - `scorecard.py` — logs/checks the weekly scorecard (active projects, proposals out, cash position)
  - `log_agent_run.py` — logs a real agent run + reviewer correction (`data/agent_run_log.json`)
  - `promote_learning.py` — surfaces repeated corrections so they get written into that agent's instructions instead of getting fixed once and forgotten
- `projects/` — actual project folders, one per active job

## Status
All 7 agents: deployment packages written, passed their scripted critical evals, still **Draft** (no Drive/system access granted — that requires the named accountable owner's sign-off per `agents/*.md`).

First real project live: `ENG-2026-001` (CE King Pkwy Hike and Bike Trail, Harris County) — used to prove the scaffold end to end.

## Quickstart
```
python3 scripts/new_project.py --name "..." --city ... --client "..." --type "..."
python3 scripts/validate_record.py --project-id ENG-2026-###
python3 scripts/run_agent_eval.py --agent A-0N
```
