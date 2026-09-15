# Scope of Work — Nueces Mosque & Residential Tower (23015)

| Div | Item | Qty | Unit | Confidence | Rate | Total | Source |
|---|---|---|---|---|---|---|---|
| 00 | Total gross building area | 77,315 | sf | cross_checked | — | — | 00 23015 GEN Permit 2025-1024.pdf p2 |
| 00 | Total dwelling units | 36 | units | single_source | — | — | 00 23015 GEN Permit 2025-1024.pdf p2 |
| | *Not independently cross-checked against a unit-by-unit schedule; single clean text extraction only.* | | | | | | |
| 00 | Total stories | 6 | stories | single_source | — | — | 00 23015 GEN Permit 2025-1024.pdf p2 |
| 03 | Pier caps, mark PC2 (36x36, over 1 pier) | 1 | ea | cross_checked | — | — | 04 23015 STRUCT Permit 2025-1023.pdf p7; 04 23015 STRUCT Permit 2025-1023.pdf p8 |
| 03 | Pier caps, mark PC3 (36x36, over 1 pier) | 4 | ea | cross_checked | — | — | 04 23015 STRUCT Permit 2025-1023.pdf p8; 04 23015 STRUCT Permit 2025-1023.pdf p7 |
| | *Page 7's own text extraction initially undercounted at 3 (likely dense-text overlap); resolved using page 8 and the vision count together, not picked arbitrarily.* | | | | | | |
| 03 | Pier caps, mark PC4 (11'-6"x11'-6", over 4 piers each) | 2 | ea | cross_checked | — | — | 04 23015 STRUCT Permit 2025-1023.pdf p7 |
| 03 | Pier caps, mark PC5 (round, over 1 pier) | 2 | ea | cross_checked | — | — | 04 23015 STRUCT Permit 2025-1023.pdf p7 |
| 03 | Pier caps, mark PC1 (24" dia, over 1 pier) | — | ea | unresolved | — | — | n/a (unresolved) |
| | *PC1 appears in the pier cap schedule (Struct p7) but was never found as an actual plan callout on any of the 3 sheets classified as foundation_plan (pages 7, 8, 26). Needs a human to check the source PDF directly — not guessed at.* | | | | | | |
| 03 | Total individual drilled piers (derived: sum of cap_count × piers-per-cap) | 15 | ea | unresolved | — | — | 04 23015 STRUCT Permit 2025-1023.pdf p7 |
| | *Marked unresolved (not cross_checked) despite having a citation, because it is INCOMPLETE by construction — excludes PC1's unknown quantity. The true total is >=15, not =15. This is a deliberate exception: a derived figure known to be a floor, not a fact.* | | | | | | |
| 08 | Interior + exterior doors, total individually-scheduled count | 85 | ea | schedule_verified | — | — | 03 23015 ARCH Permit 2025-1024.pdf p43 |
| | *Two real bugs were caught during that visual verification and fixed before this number was trusted: a hyphen missing from the location pattern silently dropped all 6 real 'MULTI-PURPOSE' doors, and a legend label sitting on the same text line as a real row (layout bleed) was briefly mislabeling one door's ID. Also flags a real data quality issue found in the source drawing itself, not introduced by extraction: door ID X102 is used twice on the exterior schedule (REAR LOBBY and, separately, a 90-min-rated STAIR door) — a likely architect numbering error, reported as-is rather than silently deduplicated. Does NOT include the 36 residential units' interior doors — see the next line.* | | | | | | |
| 08 | Interior + exterior doors, total leaf area (sum of width × height, 85 rows) | 2,511.0 | sf | schedule_verified | — | — | 03 23015 ARCH Permit 2025-1024.pdf p43 |
| 08 | Residential-unit door types (R1-R7, XR1: entry, bedroom/bath, laundry closet, closet bypass, bathroom, washer/dryer, mech closet, exterior terrace) | — | ea | unresolved | — | — | n/a (unresolved) |
| | *A RESIDENT DOOR & FRAME SCHEDULE on the same sheet (Arch p43) confirms these 8 door TYPES are used across the building's 36 units, but the sheet gives the type, not how many of each type per unit — that requires reading the actual unit floor plans, not attempted here. Confirms the scope gap flagged in the line above was real, not speculative: these doors exist, are typed, and are simply not yet counted.* | | | | | | |
| 00 | Total construction cost estimate (blended $/SF, AACE Class 4) | 77,315 | sf | benchmark_only | $260.0 | $20,101,900.0 | 00 23015 GEN Permit 2025-1024.pdf p2 |
| | *Midpoint of a $220-300/SF blended benchmark range (Austin market, Type I-A/III-A mixed construction, drilled-pier foundation, premium envelope) derived earlier this session from the real scope drivers found in these drawings — see SOP-023. NOT a vendor quote or a bottom-up sum of the line items above; those are quantities only, not yet priced, because no real unit-cost source exists for them yet (e.g. no vendor rate for a drilled pier cap of a given size). Reported as a single-point midpoint here for the table; the real range is $17.0M-$23.2M hard cost before GC/OH/fee and soft costs.* | | | | | | |
