# SOP-023 — Estimation from Client-Provided PDF Drawing Sets
Owner: Waqas (Estimator) | Reviewer: Shehab 2 / Yusuf | Status: Draft | Priority: High

## Problem this fixes
OpenConstructionERP's automated quantity takeoff needs native CAD/BIM files
(`.dwg/.rvt/.ifc/.dgn`). Almost everything ENGCO receives from architects,
engineers, and clients is a flattened PDF permit set — that's the real,
normal case, not an edge case. There is no reliable tool that converts a PDF
back into a real BIM model: PDF-to-DWG converters recover lines, not smart
objects with quantities, so feeding a converted file into the automated
pipeline would produce a confident-looking number that's actually garbage.
This SOP is the real, primary estimating path — not a fallback.

## Rule
Every estimate produced from a PDF-only set gets an explicit **AACE class**
label, and that label travels with the number everywhere it's used —
proposal, email, verbal quote. Never state a Class 5 number as if it were a
firm bid.

| Class | What it takes | Typical accuracy |
|---|---|---|
| 5 | Cover sheet + code summary only (GSF, units, stories, construction type) cross-checked against public cost-per-SF or unit-price benchmarks | Order of magnitude, ±30-50% |
| 4 | Class 5 + a pass through the major discipline sheets (civil/structural/arch) for real scope items, still benchmark-priced | Conceptual, ±20-30% |
| 3 | Full manual quantity extraction sheet-by-sheet, priced against current vendor/sub quotes or a maintained unit-cost catalog | Budget-grade, ±10-20% |

## Procedure
1. **Pull the code/area summary** from the general sheet: total gross SF,
   unit/room count, stories, occupancy type(s), construction type, sprinkler
   status. This alone supports a Class 5 estimate.
2. **Pick the right public benchmark** for the trade mix:
   - Vertical/building work: regional cost-per-SF ranges appropriate to
     construction type and occupancy.
   - Heavy civil/roadway/bridge work: public agency unit-price data (e.g.
     TxDOT Average Low Bid) by bid item and district.
3. **State the range, not a point number**, unless the client needs a single
   figure — then state the midpoint and keep the range in the backup.
4. **Escalate to Class 4/3** only when the client needs firmer numbers:
   walk the civil/structural/arch sheets discipline by discipline, extract
   real quantities (areas, lengths, counts), price against current
   quotes/catalog instead of a general benchmark.
5. **Record the methodology with the estimate** — which sheets were used,
   which benchmark source, what's excluded — so anyone reviewing it later
   can see exactly how confident to be, not just the number.
6. **Shehab 2 or Yusuf reviews and signs off** before anything above Class 5
   leaves the building to a client.

## Who owns what
- Running the extraction and benchmark pricing: Waqas
- Reviewing/signing off before client delivery: Shehab 2 (engineering scope) or Yusuf (commercial terms)

## Exit criteria for this SOP
- 3 real client estimates produced this way, each correctly labeled with its
  AACE class and assumptions, reviewed before going to a client.
