# ENGCO Estimation Team — Build Plan
Owner: Yusuf | Status: Active | Version 1.0

## Why this exists
OpenConstructionERP's automated BIM quantity takeoff was evaluated and rejected (manager decision) after real testing showed its auto-linking is unreliable — on real ENGCO-uploaded data it left quantities disconnected from any model, and on the app's own demo data it linked walls to crane-rental line items. The replacement is ours to build: tools that do the safe, mechanical work exactly, and agents that do the judgment work on a short leash, with every number traceable to a real sheet. No fine-tuning — behavior stays in editable instructions and deterministic scripts, not model weights, so it stays auditable and fixable.

This is the build-out of the **Preconstruction / Estimating** function already assigned to A-05 in `data/agent_registry.json`, and formalizes what `docs/sops/SOP-023-pdf-based-estimation.md` currently only sketches at the benchmark (Class 5/4) level.

## Already true (Phase 0 — done)
- SOP-023 exists: AACE-classed benchmark estimating from PDFs.
- Proof points: Nueces Mosque Class 4 estimate (real GSF/unit/structural data pulled by hand); Texas clinic real door + wall takeoff (254 doors, 12,475.78 m² partitions, both element-verified).
- Agent run log + promotion mechanism already built (`scripts/log_agent_run.py`, `scripts/promote_learning.py`) — this is the "learning" mechanism; no retraining involved.

## Phase 1 — Deterministic tooling foundation
**Tasks**
- Build `scripts/estimating/classify_sheets.py`: scan every page of a PDF, tag sheet type (floor plan, schedule, framing plan, code summary, etc.) by keyword match. No AI call, no cost, no invention risk.
- Build a schedule/table extractor: pull real numbers straight out of any page that's a genuine text table (code summary, door/window/finish schedules) — text extraction only, never vision, for anything already in a table.
- Define the citation schema every quantity must carry: value, unit, source sheet number, source page, confidence label.

**Milestones / exit criteria**
- Classifier correctly tags sheet types across 3 real plan sets we already have (Nueces, Texas clinic, Harris County trail), verified by hand against what we already know is on those sheets.
- Extractor correctly pulls GSF, unit count, and at least one full schedule from Nueces, matching the numbers we already manually confirmed.
- Fails if: any extracted "text" number can't be traced back to an exact source line in the PDF.

## Phase 2 — Guarded AI reading layer (DONE)
**Tasks**
- [x] Write the vision usage rule: count/identify only, never originate a precise number a schedule should provide. Written into `scripts/estimating/README.md`.
- [x] Build cross-check logic — `extract_code_summary.py`'s per-floor-sum-vs-total check, proven on real Nueces data (77,315 = 77,315, exact match).
- [x] Build a sanity-range benchmark table — `data/sanity_ranges.json` + `scripts/estimating/check_sanity.py`, tested against both a real implausible case (catches it) and the fabricated demo-data steel figure (does NOT catch it — documented honestly as a real limitation of range-checking alone).
- [x] Guarded vision read demonstrated end to end on the real Nueces foundation plan (pier cap count by mark). Found a real wrong assumption (schedule quantity misread as total instances), then found vision-cropping itself unreliable, then found text-occurrence counting is the better primary method with vision as the cross-check — the reverse of the intuitive order. See `scripts/estimating/README.md`. One genuine open gap surfaced (PC1 never found as a plan callout) and correctly left unresolved rather than guessed.

**Milestones / exit criteria**
- On a test plan set, zero invented quantities, and every cross-check flag raised is a real, correct catch (verified by human review). Met: PC3 discrepancy (3 vs 4) was a real catch, resolved with a second source, not guessed.
- Fails if: any single vision read is reported as a final number without either a citation or a flag. Met — PC1's absence was reported as an open gap, not filled in.

## Phase 3 — Output assembly (DONE)
**Tasks**
- [x] Scope-of-work output format built (`scripts/estimating/assemble_scope.py`): CSI-division structured, every line = description, quantity, unit, citation(s), confidence label. Validation enforced in code, not just convention — tested that it actually rejects an uncited line.
- [x] Pricing layer added: one clearly-labeled benchmark line (`rate_source: "benchmark"`), explicit that it is not a vendor quote and not a sum of the unpriced quantity lines above it. No fake per-line pricing invented for quantities we have no real unit-cost source for (e.g. pier caps).

**Milestones / exit criteria**
- A full run on the Nueces plan set produces a structured, fully-cited output at least as complete as today's manual Class 4 result. Met — 10 lines, `scripts/estimating/proof_runs/nueces-23015/scope_of_work.md`.
- Fails if: any line item lacks a confidence label or citation. Enforced mechanically, not just as a rule someone could forget.

## Phase 4 — Golden dataset + eval harness
**Tasks**
- Assemble a golden set: real plan sets (ideally 10+) paired with verified correct quantities — from real ENGCO past-project outcomes where available, otherwise a one-time careful manual takeoff per set (same method used on Nueces).
- Build a scoring script: per-run accuracy (% of quantities within tolerance), citation correctness, invented-quantity rate, miss rate.
- Set the numeric bar for "done" up front — not a feeling.

**Milestones / exit criteria**
- Golden set has at least 10 real plan sets with verified ground truth.
- Scoring harness runs end-to-end and produces a readable report per plan set and in aggregate.

## Phase 5 — Iterate to the bar
**Tasks**
- Run the pipeline against the full golden set; log every failure via `log_agent_run.py`.
- Promote every recurring failure into a permanent tool rule or instruction fix via `promote_learning.py` — never a one-off patch.
- Re-run the entire golden set after every round of fixes; track the score over time.

**Milestones / exit criteria**
- Hits the defined bar — **95%+ of quantities within ±5% of ground truth, 0% invented quantities, 100% citation coverage** — across the full golden set, on two consecutive full runs (not a fluke).
- Fails if: the invented-quantity rate is ever above zero. This is the one number with no tolerance.

## Phase 6 — Controlled real-world trust
**Tasks**
- Named reviewer process: reviewer checks only the items the system flagged as uncertain, not the whole document line by line.
- Run 3 real, supervised estimates on live ENGCO work, logged in the Agent Run Log.

**Milestones / exit criteria**
- 3 real supervised runs with reviewer sign-off logged before A-05's estimating scope moves off "Draft" status in `data/agent_registry.json`.
- Fails if: any output reaches a client without the named reviewer's sign-off.

## Guardrails (apply to every phase)
No invented quantities, ever — zero tolerance, not a target. Every number is either cited to a real source or explicitly marked unverified. Vision reads counts and shapes; it never originates precise figures that belong in a schedule. Fixes are permanent (promoted into rules/instructions), never one-off patches. No fine-tuning — every behavior change stays in an editable, auditable instruction or script.
