#!/usr/bin/env python3
"""Build the real Nueces Mosque & Residential Tower scope of work from
everything actually extracted and cross-checked in this session — no new
claims, only what's already been verified against the source PDFs.

Nueces is NOT an ENGCO client project (design team is pi Architects/TDi/
Blu Fish, no ENGCO involvement) — it's the real-world proof case for this
toolkit. Output goes to scripts/estimating/proof_runs/, not projects/,
which is reserved for real ENG-YYYY-### numbered ENGCO work.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_scope import build_line, assemble, to_markdown, Citation

GEN = "00 23015 GEN Permit 2025-1024.pdf"
STRUCT = "04 23015 STRUCT Permit 2025-1023.pdf"

lines = [
    build_line(
        csi_division="00", csi_division_name="General / Code Summary",
        item="Total gross building area", quantity=77315, unit="sf",
        confidence="cross_checked",
        citations=[Citation(GEN, 2, "TOTAL BUILDING GROSS SF: 77,315; cross-checked against sum of 6 per-floor areas (exact match)")],
    ),
    build_line(
        csi_division="00", csi_division_name="General / Code Summary",
        item="Total dwelling units", quantity=36, unit="units",
        confidence="single_source",
        citations=[Citation(GEN, 2, "TOTAL UNIT COUNT: 36")],
        note="Not independently cross-checked against a unit-by-unit schedule; single clean text extraction only.",
    ),
    build_line(
        csi_division="00", csi_division_name="General / Code Summary",
        item="Total stories", quantity=6, unit="stories",
        confidence="single_source",
        citations=[Citation(GEN, 2, "TOTAL: 6 STORIES")],
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Pier caps, mark PC2 (36x36, over 1 pier)", quantity=1, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(STRUCT, 7, "Schedule row PC2 + 1 plan callout, text-occurrence method"),
            Citation(STRUCT, 8, "Confirmed on second foundation-plan sheet"),
        ],
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Pier caps, mark PC3 (36x36, over 1 pier)", quantity=4, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(STRUCT, 8, "4 plan callouts via text-occurrence method, matching vision count"),
            Citation(STRUCT, 7, "Vision count of 4 distinct plan locations (Family Toilet, REC 101, and 2 along south curved wall)"),
        ],
        note="Page 7's own text extraction initially undercounted at 3 (likely dense-text overlap); resolved using page 8 and the vision count together, not picked arbitrarily.",
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Pier caps, mark PC4 (11'-6\"x11'-6\", over 4 piers each)", quantity=2, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(STRUCT, 7, "2 plan callouts (Sister's Wudu side + Brother's Wudu side, mirrored), text + vision agree"),
        ],
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Pier caps, mark PC5 (round, over 1 pier)", quantity=2, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(STRUCT, 7, "2 plan callouts (Gallery C101 + Gallery C100, mirrored), text + vision agree"),
        ],
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Pier caps, mark PC1 (24\" dia, over 1 pier)", quantity=None, unit="ea",
        confidence="unresolved",
        citations=[],
        note="PC1 appears in the pier cap schedule (Struct p7) but was never found as an actual plan callout on any of the 3 sheets classified as foundation_plan (pages 7, 8, 26). Needs a human to check the source PDF directly — not guessed at.",
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Deep Foundations",
        item="Total individual drilled piers (derived: sum of cap_count × piers-per-cap)",
        quantity=15, unit="ea",
        confidence="unresolved",
        citations=[
            Citation(STRUCT, 7, "PC2(1×1) + PC3(4×1) + PC4(2×4) + PC5(2×1) = 15; excludes PC1, which is unresolved"),
        ],
        note="Marked unresolved (not cross_checked) despite having a citation, because it is INCOMPLETE by construction — excludes PC1's unknown quantity. The true total is >=15, not =15. This is a deliberate exception: a derived figure known to be a floor, not a fact.",
    ),
]

lines.append(build_line(
    csi_division="00", csi_division_name="Summary / Pricing",
    item="Total construction cost estimate (blended $/SF, AACE Class 4)",
    quantity=77315, unit="sf",
    confidence="benchmark_only",
    unit_rate=260.00, rate_source="benchmark",
    citations=[Citation(GEN, 2, "Applied to the cross-checked 77,315 SF total above")],
    note=("Midpoint of a $220-300/SF blended benchmark range (Austin market, Type I-A/III-A "
          "mixed construction, drilled-pier foundation, premium envelope) derived earlier this "
          "session from the real scope drivers found in these drawings — see SOP-023. NOT a "
          "vendor quote or a bottom-up sum of the line items above; those are quantities only, "
          "not yet priced, because no real unit-cost source exists for them yet (e.g. no vendor "
          "rate for a drilled pier cap of a given size). Reported as a single-point midpoint here "
          "for the table; the real range is $17.0M-$23.2M hard cost before GC/OH/fee and soft costs."),
))

scope = assemble("Nueces Mosque & Residential Tower (23015)", lines)

out_dir = Path(__file__).resolve().parent / "proof_runs" / "nueces-23015"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scope_of_work.json").write_text(json.dumps(scope, indent=2) + "\n")
(out_dir / "scope_of_work.md").write_text(to_markdown(scope) + "\n")

print(f"Assembled {scope['line_count']} lines, all valid (citation + confidence present, or explicitly unresolved).")
print(f"Written to {out_dir}/")
