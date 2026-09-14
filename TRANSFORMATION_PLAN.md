# ENGCO ONE — Company Transformation Plan
Owner: Joseph (IT / Systems) | Status: Active | Version 1.0

## Goal
Take ENGCO from ad-hoc, undocumented operations to a structured company running on one shared system: standard SOPs, real tracking, and seven bounded AI agents that draft and organize work while named humans retain every controlled decision.

## Frameworks this is built on (not invented from scratch)
- **EOS (Entrepreneurial Operating System)** — company operating rhythm: Vision/Traction Organizer, Accountability Chart, quarterly Rocks, weekly Scorecard, Level-10 meetings. Standard for firms at ENGCO's size and stage.
- **AEC/construction industry project lifecycle** (AIA phase model + standard CM practice) — Intake → Feasibility → Design → Permitting → Preconstruction → Construction → Closeout.
- **ISO 9001 document-control principles** — every controlled document has one owner, one approver, one approved version, a review cadence, and a lifecycle: Draft → Under Review → Approved → Retired.

## Current state (Phase 0 — done)
- Drive system of record built: Agent Registry, company-wide + 7 specialized agent instructions, 10-template operating pack, Roles & Access Matrix, Portfolio Register, Knowledge/SOP Register (22-item backlog, all "Missing").
- `engco-one` GitHub repo live: same content as JSON/Markdown, 3 working automation scripts (`new_project.py`, `validate_record.py`, `run_agent_eval.py`).
- All 7 agents: deployment packages written, passed scripted critical evals. Status: **Draft**. No real system access granted to any agent.
- One test project (ENG-2026-001, a real public Harris County civil project) scaffolded and validated end to end — proves the mechanics work.
- Zero real employees onboarded. Zero real ENGCO projects in the system. Zero SOPs written (only cataloged).

## Phase 1 — Governance activation (DONE)
- Accountability Chart built with real names: `docs/accountability_chart.md`. Seats are functional accountability, not formal departments — decision recorded, revisit at higher headcount.
- Scope call: full 7-agent / 22-SOP rollout is over-built for current headcount (~8, everyone-does-everything). Deferred to Phase 5. Lean start below is the real Phase 2/3.
- Deferred: formal V/TO and quarterly Rocks — revisit once the lean rhythm (below) is running for a few weeks, not before.

## Phase 2 — Lean start (replaces original Phase 2 scope)
**Milestones**
- Weekly scorecard: active projects, proposals out, cash position — one shared number set, reviewed weekly.
- Two SOPs only:
  - SOP-001 Project intake & numbering — fixes Shehab 1 / Waqas both touching leads with no single owner.
  - Daily field reporting — fixes Shawqi having zero backup or record from the field.
- One agent to Pilot: A-05 (Construction/Field) — drafts field reports for Shawqi's review only. No other agent moves off Draft in this phase.

**Evaluation / exit criteria**
- Scorecard reviewed weekly for 3 consecutive weeks, not skipped.
- Both SOPs at "Approved" with named owner sign-off.
- A-05 has 5 supervised runs logged with human corrections captured.
- Fails if: scorecard goes stale, or A-05 output is used without Shawqi's review.

## Phase 3 — First real pilot (live project, not a sample)
**Milestones**
- Run one actual ENGCO client project through the full system: real folder, real controls record, real registry row, real SOPs applied at each phase gate.
- Agents operate in supervised Draft mode only — every output reviewed by the named owner before use.
- Log every material agent run in the Agent Run Log; capture friction points and corrections.

**Evaluation / exit criteria**
- Project moves through at least 2 real phase gates using the system, with evidence logged at each gate per `project_registry.json`.
- Fails if: any agent output was used without human review, or a phase gate was marked complete without the required evidence.

## Phase 4 — Agent Draft → Pilot → Active
**Milestones**
- Based on Phase 3 evidence, each accountable owner formally moves their agent from Draft to Pilot (grants scoped Drive/repo access) per the gate in that agent's deployment package.
- Run multiple supervised Pilot cycles on real work.
- Move to Active only after Pilot shows reliable source use, correct handoffs, and correct escalation behavior.

**Evaluation / exit criteria**
- Per agent: accountable owner + backup owner named, scope approved, all required evals re-passed post-Pilot, review cadence set.
- Fails if: an agent is marked Active without a supervised Pilot run on real work.

## Phase 5 — Company-wide rollout
**Milestones**
- Onboard remaining employees with access scoped per the Roles & Access Matrix (least privilege, not blanket access).
- Write the remaining 7 Medium-priority SOPs (SOP-002, 014, 017-021).
- Weekly Scorecard (Portfolio Dashboard) and Level-10-style weekly meeting become the actual operating rhythm, not a document nobody opens.

**Evaluation / exit criteria**
- 100% of active projects have a current registry row updated within 7 days (enforced by `validate_record.py`'s staleness check).
- Fails if: Portfolio Dashboard shows stale or missing data for any active project.

## Phase 6 — Continuous improvement
**Recurring, not a one-time milestone**
- Quarterly Rocks review and reset.
- SOP review cadence per each document's assigned frequency.
- Re-run agent evals after any material change to instructions, access, tools, or model.
- Closeout lessons-learned feed back into templates and SOPs — the loop that keeps this from going stale again.

## Guardrails that apply across every phase
No agent independently approves scope, price, schedule, contract terms, design, permit interpretation, field direction, safety action, or external communication. Every controlled decision has one named human owner. Stale status is not reliable status — `validate_record.py` enforces this mechanically, not by trust.
