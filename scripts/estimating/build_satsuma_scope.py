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
        item="Number of buildings on site", quantity=None, unit="ea",
        confidence="unresolved",
        citations=[],
        note=("Visually read as '2' on the Harris County Engineering Dept. Review Sheet ('BUILDING "
              "PERMITS (NO. OF BUILDINGS = 2)'), but that field is NOT in the PDF's extractable text "
              "layer — same raster-template issue as the HCFCD sheet, but this particular field has "
              "no known-position schema built yet. Not reported as a hard number per this toolkit's "
              "own rule: vision identifies, it doesn't originate a number a report relies on. A human "
              "should confirm this directly against the sheet before using it."),
    ),
]

scope = assemble("6659 Satsuma Dr Warehouse (ENG-2026-004)", lines)

out_dir = Path(__file__).resolve().parent.parent.parent / "projects" / "ENG-2026-004-6659-Satsuma-Dr-Warehouse-Houston" / "05 - Preconstruction"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scope_of_work.json").write_text(json.dumps(scope, indent=2) + "\n")
(out_dir / "scope_of_work.md").write_text(to_markdown(scope) + "\n")

print(f"Assembled {scope['line_count']} lines, all valid (citation + confidence present, or explicitly unresolved).")
print(f"Written to {out_dir}/")
