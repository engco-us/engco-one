#!/usr/bin/env python3
"""Build the real ENG-2026-004 (6659 Satsuma Dr Warehouse, Houston) scope
from the actual civil plan set — no new claims, only what's cited to real
extracted text or the real extract_hcfcd_detention.py output.

REPORT-ONLY. Quantities for a human to review — nothing here submits,
prices, or approves anything.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_scope import build_line, assemble, to_markdown, Citation

PLANS = "Civil Plans - 6659 SATSUMA DR HOUSTON TX 77041- 8.25.2026..pdf"
PLANS_ABS = "/Users/yusuf/Downloads/Civil Plans   - 6659 SATSUMA DR HOUSTON TX 77041- 8.25.2026..pdf"

# Real extractor output, not retyped by hand.
result = json.loads(subprocess.run(
    [sys.executable, str(Path(__file__).parent / "extract_hcfcd_detention.py"), PLANS_ABS, "--page", "3"],
    capture_output=True, text=True, check=True,
).stdout)
assert result["is_hcfcd_review_sheet"] and result["rows"], "extractor did not return the expected table"

UNIT_BY_ROW = {
    "Maximum allowable outflow (pre-development peak flow), cfs": "cfs",
    "Maximum outflow provided (peak flow from basin), cfs": "cfs",
    "Design water surface elevation, ft": "ft",
    "Minimum storage required, ac-ft": "ac-ft",
    "Detention storage provided, ac-ft": "ac-ft",
    "Storage rate provided, ac-ft/ac": "ac-ft/ac",
    "Outflow velocity into channel, ft/sec": "ft/sec",
}

lines = [
    build_line(
        csi_division="02", csi_division_name="Existing Conditions / Survey",
        item="Site area", quantity=1.302, unit="acres",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, "1.302 ACRES (56,700 SF) — Property Description panel, item II.A")],
        note="56,700 SF, same value. Lot 48, Block 5, Satsuma Estates Sec. 2.",
    ),
]

# One line per detention-table row, at the 100-year (1% exceedance) design
# storm — the governing regulatory value — with the other two return
# periods carried in the note so nothing from the real table is dropped.
for row in result["rows"]:
    label = row["row"]
    cols = row["columns"]
    unit = UNIT_BY_ROW[label]
    lines.append(build_line(
        csi_division="33", csi_division_name="Utilities — Stormwater Detention",
        item=f"{label.split(',')[0]} (1% / 100-year)", quantity=cols["1% exceedance (100-year)"], unit=unit,
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, f"HCFCD PCPM Summary Table, row '{label}' — real extractor output, scripts/estimating/extract_hcfcd_detention.py")],
        note=f"Full row: 2-year={cols['50% exceedance (2-year)']} {unit}, 10-year={cols['10% exceedance (10-year)']} {unit}, 100-year={cols['1% exceedance (100-year)']} {unit}.",
    ))

lines += [
    build_line(
        csi_division="33", csi_division_name="Utilities — Stormwater Detention",
        item="Pumped 1% exceedance storage volume", quantity=0.473, unit="ac-ft",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, "0.473 ACFT, 0.42% of total volume — Additional Criteria for Pumped Detention Basins")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Stormwater Detention",
        item="Pumped-basin drain time", quantity=5.72, unit="hours",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, "Drain time for basin = 5.72 hours — Additional Criteria for Pumped Detention Basins")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Stormwater Detention",
        item="Flow restrictor — outlet pipe size", quantity=18, unit="in",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, "Outlet pipe size: 18-inch — Flow Restrictor Size panel")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Stormwater Detention",
        item="Flow restrictor — restrictor pipe size", quantity=4, unit="in",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 3, "Restrictor pipe size: 4-inch, restrictor plate 4-inch diameter circular orifice — Flow Restrictor Size panel")],
    ),
    build_line(
        csi_division="00", csi_division_name="General",
        item="Number of buildings on site", quantity=2, unit="ea",
        confidence="cross_checked",
        citations=[Citation(PLANS, 7, "'PROP. BUILDING 1' and 'PROP. BUILDING 2' — two distinct, real labeled callouts on the C2.1 Site Plan")],
        note=("Originally left unresolved because the count printed on the Harris County Engineering "
              "Dept. Review Sheet ('NO. OF BUILDINGS = 2') isn't in that page's extractable text layer. "
              "Resolved properly instead of left stuck: the real Site Plan (C2.1) independently confirms "
              "2 buildings via its own real text labels — same number, second real source, now trustworthy."),
    ),

    # --- Building & yard areas, real text off the C2.1 Site Plan (sheet 4/22, PDF page 7) ---
    build_line(
        csi_division="03", csi_division_name="Concrete / Building Slabs",
        item="Building 1 footprint (Warehouse 1: 3,000 SF + Office: 3,000 SF)", quantity=6000, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 7, "PROP. BUILDING 1, 6000 SQ.FT. (PROP. WAREHOUSE 1 3,000 SQ.FT. + OFFICE 3,000 SQ.FT.), FF=117.0' — C2.1 Site Plan")],
    ),
    build_line(
        csi_division="03", csi_division_name="Concrete / Building Slabs",
        item="Building 2 footprint (Warehouse 2: 3,000 SF + Office: 3,000 SF)", quantity=6000, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 7, "PROP. BUILDING 2, 6000 SQ.FT. (PROP. WAREHOUSE 2 + OFFICE 3,000 SQ.FT.), FF=117.0' — C2.1 Site Plan")],
        note="Total building footprint, both buildings combined: 12,000 SF. Slab thickness/type not shown on this sheet — needed for a concrete volume, not just footprint area.",
    ),
    build_line(
        csi_division="32", csi_division_name="Exterior Improvements — Paving",
        item="Laydown yard 1 area", quantity=2500.0, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 7, "PROP. LAYDOWN YARD 1, 2500.0 SQ.FT. — C2.1 Site Plan")],
    ),
    build_line(
        csi_division="32", csi_division_name="Exterior Improvements — Paving",
        item="Laydown yard 2 area", quantity=2000.0, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(PLANS, 7, "PROP. LAYDOWN YARD 2, 2000.0 SQ.FT. — C2.1 Site Plan")],
    ),
    build_line(
        csi_division="32", csi_division_name="Exterior Improvements — Paving",
        item="Parking spaces", quantity=None, unit="ea",
        confidence="unresolved",
        citations=[],
        note=("'PROP. 10 PARKING' is printed twice on the C2.1 Site Plan, once near each building — "
              "real text, but genuinely ambiguous whether that's 10 total (one shared count referenced "
              "twice) or 10 per side (20 total). Stall-by-stall counting off the full-size plan would "
              "resolve it; not guessed at here."),
    ),

    # --- Storm sewer pipe, real text, cross-checked across two independent sheets ---
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Storm sewer pipe, 18-inch HDPE", quantity=524.8, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 9, "7 real pipe-run callouts (26.4, 197.2, 180.4, 29.0, 14.7, 7.1, 70.0 LF) — C3.1 Detention Pond Details Plan"),
            Citation(PLANS, 10, "Same 7 pipe runs, identical lengths — C4 Drainage Plan, independent sheet"),
        ],
        note=("Sum of 7 real labeled segments. Cross-checked: the same 7 runs, same lengths, appear on "
              "two independently drawn sheets (C3.1 and C4) and agree exactly. Caught a real error doing "
              "this properly: an earlier visual read of one segment said '70.0 LF 14\" HDBE' — the real "
              "text says '70.0 LF 18\" HDPE'. Text corrected the vision misread, exactly per this "
              "toolkit's own rule (text is the source of truth, vision never overrides it). Does NOT "
              "include an 8th 18\" HDPE value ('11.4 LF @ 0.22%') found on this same sheet's Section A-A "
              "profile — see the separate unresolved line below; it's flagged out rather than silently "
              "folded into this cross-checked figure."),
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Possible additional 18-inch HDPE segment (unconfirmed)", quantity=None, unit="lf",
        confidence="unresolved",
        citations=[Citation(PLANS, 9, "11.4 LF 18\" HDPE @ 0.22% — printed in the Section A-A profile detail, C3.1 Detention Pond Details Plan")],
        note=("A real, found gap in this report's first pass, disclosed rather than left buried: this "
              "value was silently dropped from the original 7-segment total without being checked. "
              "Re-verified now — it does NOT appear anywhere on the independent C4 Drainage Plan (the "
              "sheet that cross-confirmed the other 7 segments), and no matching label exists in the "
              "plan view either. Two explanations are equally plausible without the CAD file: a real 8th "
              "pipe run inside the pond structure that the plan view never separately labeled, or a "
              "partial/illustrative sub-length of a segment already counted, shown only for the "
              "profile's own elevation bookkeeping. If real and additional, total 18\" HDPE would be "
              "536.2 LF, not 524.8. Not guessed either way — a human should trace Section A-A against "
              "the plan view directly, or check the CAD file, before pricing."),
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Storm sewer pipe, 15-inch HDPE", quantity=133.0, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 9, "133.0 LF 15\" HDPE @ 0.30% — C3.1 Detention Pond Details Plan"),
            Citation(PLANS, 10, "Same segment, same length — C4 Drainage Plan"),
        ],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Storm sewer pipe, 12-inch HDPE", quantity=132.9, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 9, "132.9 LF 12\" HDPE @ 0.30% — C3.1 Detention Pond Details Plan"),
            Citation(PLANS, 10, "Same segment, same length — C4 Drainage Plan"),
        ],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Restrictor pipe, 4-inch PVC", quantity=6.0, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 9, "6.0 LF 4\" PVC RESTRICT @ 0.11% — C3.1 Detention Pond Details Plan"),
            Citation(PLANS, 10, "Same segment, same length — C4 Drainage Plan"),
        ],
        note="Matches the 4-inch restrictor pipe size already confirmed from the HCFCD Review Sheet — a third independent agreement on this one dimension.",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Storm Sewer",
        item="Total storm sewer pipe, all sizes (confirmed segments only)", quantity=796.7, unit="lf",
        confidence="cross_checked",
        citations=[Citation(PLANS, 9, "Sum of the 10 cross-checked segments above (7×18\", 1×15\", 1×12\", 1×4\")"), Citation(PLANS, 10, "Same total, independently confirmed on C4")],
        note="Excludes the unconfirmed 11.4 LF segment above. If that turns out to be real and additional, the true total is 808.1 LF, not 796.7.",
    ),

    # --- Real, honest gaps: not measured this pass ---
    build_line(
        csi_division="32", csi_division_name="Exterior Improvements — Paving",
        item="Concrete parking / pavement area", quantity=None, unit="sf",
        confidence="unresolved",
        citations=[],
        note=("The C2.1 Site Plan legend distinguishes 'CONCRETE PARKING' from 'PAVEMENT' as two real, "
              "different hatch patterns, and both are drawn on the plan — but no dimensioned area or "
              "table was found for either in this pass. Measuring it requires either the CAD file or a "
              "real area take-off traced against the plan's own graphic scale, not attempted here."),
    ),
    build_line(
        csi_division="31", csi_division_name="Earthwork",
        item="Cut / fill volume", quantity=None, unit="cy",
        confidence="unresolved",
        citations=[],
        note="C5 Grading Plan and C6 Grading Details exist in this set (sheets 8-9) but weren't checked for a cut/fill summary in this pass — flagged for the next pass, not assumed zero.",
    ),
]

scope = assemble("6659 Satsuma Dr Warehouse (ENG-2026-004)", lines)

out_dir = Path(__file__).resolve().parent.parent.parent / "projects" / "ENG-2026-004-6659-Satsuma-Dr-Warehouse-Houston" / "05 - Preconstruction"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scope_of_work.json").write_text(json.dumps(scope, indent=2) + "\n")
(out_dir / "scope_of_work.md").write_text(to_markdown(scope) + "\n")

print(f"Assembled {scope['line_count']} lines, all valid (citation + confidence present, or explicitly unresolved).")
print(f"Written to {out_dir}/")
