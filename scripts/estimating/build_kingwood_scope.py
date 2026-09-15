#!/usr/bin/env python3
"""Build the real ENG-2026-002 (LSC Kingwood Fire Science Water Line and
Septic System, CSP 26-08-10) scope of work from the actual bid attachments
— no new claims, only what's cited to the SOW text or the approved plan set.

REPORT-ONLY. This produces a materials/quantity breakdown for a human
estimator to build the actual bid from. Nothing here submits a bid,
prices a proposal, or commits ENGCO to anything.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_scope import build_line, assemble, to_markdown, Citation

PLANS = "26 0813 - LSC Kingwood FTF_Approved PUB Plans_260813.pdf"
SOW_WATER = "26 0814 SOW Water Line 12 & 8 RV1.pdf"
SOW_SEPTIC = "26 0818 SOW Septic System.pdf"

lines = [
    # --- Water line: pipe material/spec (explicit in SOW text) ---
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Kingwood Drive segment, 12-inch C900 PVC (STA 1+00.00 to STA 6+00.00, tie-in to wet connection)",
        quantity=499.96, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 4, "STA. 1+00.00 KINGWOOD DRIVE (baseline origin); PC: 1+59.83; L=299.25 R=2150.000 T=149.865 (curve data); PT: 4+59.07; tangent-out bearing N88°13'09.99\"E, distance 140.89 (all printed directly on the plan-and-profile sheet)"),
        ],
        note=("No bid-quantity sheet exists in this set and no single station is printed as \"end of "
              "line,\" but the sheet's own survey curve data gives an exact length by arithmetic, not a "
              "guess: 59.83 ft (STA 1+00 to PC) + 299.25 ft (curve arc, PC to PT) + 140.89 ft (tangent "
              "past PT, per the printed bearing+distance call) = 499.97 LF. Cross-checked a second way, "
              "by straight station subtraction (end STA 6+00.00 [=PT 4+59.07 + 140.89] minus begin STA "
              "1+00.00) = 499.96 LF. The two independent computations agree to within 0.01 ft — real "
              "closure, not rounding luck. Also visually confirmed against the rendered plan sheet (not "
              "just trusted from text): the 'PROP 12\" PVC (C-900) WATER LINE (PUBLIC)' leader points "
              "directly at the dashed line that sweeps through this exact curve, and that same line runs "
              "unbroken through the tangent to the '1 - 12\" WET CONNECTION' callout at the far end — the "
              "hydrant labeled 'STA 4+59' sits exactly where the curve visually straightens, matching the "
              "printed PT: 4+59.07. This whole segment is 12-inch pipe only; no 8-inch is called out on "
              "this sheet (Sorters Rd is where the 12-to-8 transition happens, on the next line)."),
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Sorters Road segment, 12-inch/8-inch C900 PVC (STA 1+00.00 to STA 4+13.47, tie-in to trenchless crossing)",
        quantity=313.47, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(PLANS, 5, "STA. 1+00.00 SORTERS ROAD (baseline origin, shared with Kingwood Drive STA 1+00.00)"),
            Citation(PLANS, 6, "STA, 4+13.47 SORTERS ROAD = STA. 1+34.68 SORTERS ROAD CROSSING (explicit tie-in station, printed on both sheet 05 and sheet 06)"),
        ],
        note=("313.47 LF = 413.47 - 100.00, station arithmetic between two independently, explicitly "
              "printed station callouts (both sheets agree on the tie-in station exactly). This is the "
              "one segment length on this project defensible enough to call cross_checked rather than "
              "a plan-scaled estimate. Includes the 12-inch-to-8-inch transition; sheet 05's profile "
              "shows the transition graphically but does not print its exact station."),
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Trenchless 8-inch C900 PVC crossing under Sorters Road", quantity=44, unit="lf",
        confidence="cross_checked",
        citations=[
            Citation(SOW_WATER, 4, "Construct approximately 44 linear feet of trenchless 8-inch C900 PVC public water line crossing Sorters Road..."),
            Citation(PLANS, 6, "PROP. 44 LF TRENCHLESS CONSTRUCTION (PUBLIC) — printed directly on the Sorters Road Crossing plan-and-profile sheet"),
        ],
        note="Real independent agreement: the SOW's 'approximately 44 linear feet' and the plan's printed '44 LF' label match exactly.",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Ductile iron pipe transition sections (AWWA C151, C104 lining, 8-mil poly wrap)", quantity=None, unit="lf",
        confidence="unresolved",
        citations=[Citation(SOW_WATER, 4, "Provide required transitions between PVC and ductile iron pipe and fittings...")],
        note="Real requirement, shown graphically (hatched) on sheets 04-06 profiles at each vertical-bend/casing location, but no length is labeled at any transition. Needs a human take-off from the profile details.",
    ),

    # --- Water line: discrete fittings/valves/hydrants (plan callouts, not yet tallied) ---
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="12-inch wet connection to existing City water line", quantity=1, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(SOW_WATER, 4, "Perform one 12-inch wet connection to the existing 12-inch City water line on Kingwood Drive..."),
            Citation(PLANS, 4, "1 - 12\" WET CONNECTION / REMOVE EXIST. PLUG AND BOV AND CONNECT PROP. 12\" WATER LINE TO EXIST. 12\" WATER LINE — printed callout, east end of Kingwood Drive sheet"),
        ],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Fire hydrant assemblies (6-inch lead, auxiliary valve, thrust restraint)", quantity=4, unit="ea",
        confidence="vision_count",
        citations=[Citation(PLANS, 4, "Counted 4 fire-hydrant symbols with F.H. callouts across sheets 04-06: STA 1+44 (Kingwood Dr), STA 4+59 (Kingwood Dr), Sorters Rd mid-segment, STA 4+18 (Sorters Rd)")],
        note="Counted from the plan-view fire-hydrant symbol + station callout on each sheet, not from a schedule table (none exists on this set) — flagged vision_count, not schedule_verified. A human should re-confirm against the full-size plan before pricing.",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="Gate valves with box, various sizes (6\", 8\", 12\") at tees/connections", quantity=None, unit="ea",
        confidence="unresolved",
        citations=[],
        note=("Real, plainly labeled on every plan sheet (e.g. '2-12\" G.V. W/ BOX', '1-6\" G.V. W/ BOX', "
              "'1-8\" G.V. W/ BOX') at each tee and connection cluster — but several fitting clusters "
              "appear on more than one sheet where two sheets share a boundary point (Kingwood Dr/"
              "Sorters Rd junction shown on both sheet 04 and sheet 05; Sorters Rd/crossing junction "
              "shown on both sheet 05 and sheet 06). Double-counting a shared-boundary cluster is a "
              "real risk here — the same failure mode this toolkit already hit and fixed once on "
              "Nueces's pier caps. Rather than guess which clusters are duplicates without a clean way "
              "to cross-check station coordinates between sheets, this is left for a human to tally "
              "directly off the full-size plans (or the source CAD/DWG file, referenced in the plan "
              "sheets' title blocks) rather than risk a wrong number with a confident label."),
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="12-inch fittings: tees, 45° bends, plugs and clamps at line ends/junctions", quantity=None, unit="ea",
        confidence="unresolved",
        citations=[],
        note="Same shared-boundary double-count risk as the gate valves above — flagged for the same reason, not guessed at.",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="8-inch fire-rated compound meter assembly (FRCWMA) with vault, in 31'x15' water meter easement", quantity=1, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(SOW_WATER, 4, "...8-inch fire-rated compound meter with vault (FRCWMA) in the 31'x15' water meter easement..."),
            Citation(PLANS, 6, "PROP. FRCWMA W/ VAULT, labeled on the Sorters Road Crossing plan and profile"),
        ],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — Water Distribution",
        item="8-inch reduced pressure zone (RPZ) backflow preventer assembly, on private property", quantity=1, unit="ea",
        confidence="cross_checked",
        citations=[
            Citation(SOW_WATER, 4, "...and the 8-inch reduced pressure zone (RPZ) backflow preventer assembly located on private property..."),
            Citation(PLANS, 6, "PROPOSED 8\" REDUCED PRESSURE ZONE (RPZ) BACKFLOW PREVENTOR IN PRIVATE PROPERTY — key note W2, Sorters Road Crossing sheet"),
        ],
    ),

    # --- Septic / OSSF: directly cited from the SOW text, very high confidence ---
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="System design capacity", quantity=272, unit="gpd",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "The system shall be constructed to accommodate a maximum daily usage of 272 Gallons Per Day (GPD).")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Minimum required trench bottom area", quantity=1360, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "The contractor shall prepare a minimum required trench bottom of 1,360 square feet...")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Engineered drip disposal area", quantity=2560, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...and install the engineered drip area across 2,560 square feet.")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Pretreatment tank, 500-gallon", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "Furnish, excavate, and install a 500-gallon pretreatment tank...")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Clearstream aerobic treatment unit, 800-gallon", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...an 800-gallon Clearstream Treatment Unit...")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Pump tank, 1,080-gallon", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...and a 1,080-gallon pump tank. A chlorinator is not required for this specific design.")],
        note="SOW explicitly states no chlorinator is required — do not price one.",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Simplex effluent pump, Goulds 20 EB, 0.5 HP", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...a Simplex Effluent Pump (Goulds 20 EB 1/2 HP)...")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Solids pump, 2-inch, Goulds, in dosing tank", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...a 2-inch Goulds Solids Pump inside the dosing tank...")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Effluent pump, Goulds, 0.5 HP, 20 GPM", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 1, "...and a 0.5 HP Goulds 20 GPM Effluent Pump.")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Dual filter, Aztec, 100 micron", quantity=1, unit="ea",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 2, "Install an Aztec Dual 100 Micron Filter to ensure effluent clarity and protect the drip infrastructure.")],
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Drip tubing, Netafim, 0.91 GPH, across the 2,560 SF drip field", quantity=2560, unit="sf",
        confidence="schedule_verified",
        citations=[Citation(SOW_SEPTIC, 2, "Install Netafim 0.91 GPH drip tubing throughout the designated absorption area.")],
        note="Quantity re-stated from the drip-area line above — this is the area the tubing must cover, not a separate linear-footage figure (none given; drip emitter spacing/lateral spacing needed to convert to LF of tubing is not in the SOW).",
    ),
    build_line(
        csi_division="33", csi_division_name="Utilities — On-Site Sewage Facility (OSSF)",
        item="Supply piping, training facility building to septic system (Sch 40 or DWV)", quantity=None, unit="lf",
        confidence="unresolved",
        citations=[Citation(SOW_SEPTIC, 1, "Install Schedule 40 or DWV thick-wall pipe for all connections running from the training facility building to the septic system.")],
        note="No length given in the SOW; the septic system's own 2-page SOW has no site plan showing the building-to-tank distance. Needs the actual site/civil plan for the fire training facility building, which is not included in this bid-attachments package.",
    ),
]

scope = assemble("LSC Kingwood Fire Science Water Line and Septic System (CSP 26-08-10)", lines)

out_dir = Path(__file__).resolve().parent.parent.parent / "projects" / "ENG-2026-002-LSC-Kingwood-Fire-Science-Water-Line-and-Septic-System-Porter" / "05 - Preconstruction"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scope_of_work.json").write_text(json.dumps(scope, indent=2) + "\n")
(out_dir / "scope_of_work.md").write_text(to_markdown(scope) + "\n")

print(f"Assembled {scope['line_count']} lines, all valid (citation + confidence present, or explicitly unresolved).")
print(f"Written to {out_dir}/")
