# Estimating Toolkit

Phase 1 of `ESTIMATING_TEAM_PLAN.md`: deterministic tools that do the parts
of a takeoff that don't need judgment, so an agent never has to re-derive
them from scratch (and never has a chance to invent them).

## Tools

**`classify_sheets.py`** — scans every page of a discipline PDF and tags
its sheet type (floor plan, schedule, framing plan, code summary, etc.) by
keyword match. No model call, no cost, no invention risk.

**`render_sheet.py`** — renders one PDF page to an image at a tested DPI,
for vision reading. The only sanctioned way to get a sheet in front of a
vision model in this pipeline — see the VISION RULE below before using it.

**`check_sanity.py`** — flags an extracted quantity as implausible if it
falls outside a typical range for its category (`data/sanity_ranges.json`).
Catches wildly-wrong values (wrong units, misread digit) cheaply. **Does
not catch a moderately-wrong-but-plausible number** — tested against the
fabricated 620,000 kg steel figure from the OpenConstructionERP demo data
(see chat history 2026-09-14): it lands at 10.4 lb/sf, comfortably inside
the normal 6-40 range, so this check alone would **not** have caught it.
Range-checking is a cheap secondary catch, not a substitute for citations
and cross-checks — those stay the primary defense against invented numbers.

**`extract_code_summary.py`** — pulls known code-summary fields (gross
building SF, unit count, stories, per-floor areas) off a general/cover
sheet, with an exact citation for every value — and runs a real
cross-check: do the per-floor areas actually sum to the stated total?
Uses `pdftotext -layout` (preserves column position), which was necessary:
plain-mode text interleaves multiple tables unpredictably when the same
label ("FIRST FLOOR:") appears in two different tables on one sheet.

**`extract_door_schedule.py`** — pulls door ID, location, width, and
height off an architectural door & frame schedule. One ID pattern and row
structure covers every door-numbering scheme found on the same real sheet
(plain 3-digit room-based IDs, `C###`/`ST###`/`X###` prefixed IDs, and
`R#`/`XR#` unit door TYPE codes) — see the "Trust the render, not the
regex" lesson below for how its first version was wrong and got caught.

**`extract_hcfcd_detention.py`** — pulls the 7-row detention-basin summary
table off a Harris County Flood Control District "Review Sheet", a
standardized county form reused across every HCFCD-jurisdiction civil
project, not project-specific. Real, novel difference from every other
extractor here: the row/column LABELS aren't in the PDF's text layer at
all (baked into a raster template background) — only the engineer-filled
VALUES are real text. So this is position-based, not label-anchored, and
correspondingly more fragile if the county revises the form; guarded by
refusing to run unless the page's real text confirms it's actually this
form, and refusing to map values unless exactly the expected row count is
found. Proven on a real project (6659 Satsuma Dr, Houston — HC Project
2607210179).

**`auto_extract.py`** — tries every extractor above that this toolkit has
real proof on (COMcheck, REScheck, TxDOT E&Q, door schedules, HCFCD
detention sheets) against one
PDF and reports only the ones that actually matched, with an honest note
when none did. Exists because `classify_sheets.py` alone is NOT a
quantity takeoff — it tags what's on each page and never produces a
number, and a product surface once shipped that confused the two (a
"Quantity Takeoff" screen that only ran classification and showed a user
a list of page tags with no quantities on it, live, in front of the
user — see the product's own commit history). This is the fix: run
everything real, say plainly when nothing matched, never let
classification stand in for extraction.

## VISION RULE (Phase 2 guardrail)

Vision is allowed to **count and identify** — how many, roughly what kind,
is this present. Vision is **never allowed to originate a precise number**
that should come from a schedule or a labeled dimension. If a precise
number matters and there's no table for it, that's a flagged gap for a
human to resolve — not a vision guess reported as a fact. This rule exists
because vision reads on tiny CAD dimension text are unreliable in exactly
the way schedule text extraction isn't; the failure mode to avoid is a
confident-looking wrong number with no way to tell it apart from a right one.

## The citation rule every tool here follows

Every extracted value carries:
- `value` — the actual number/text, exactly as it appears in the source
- `source_file`, `source_page` — exactly where it came from
- `source_snippet` — the actual matched text, so a human can verify in
  one glance without re-opening the PDF
- `confidence` — `"high"` (found and matched cleanly) or `"not_found"`
  (label exists or was expected, but no value could be confirmed — this is
  reported honestly, never filled in with a guess or a nearby unrelated
  number)

## Validated against real data (2026-09-14)

Both tools were run against the real Nueces Mosque & Residential Tower
100% CD permit set (6 discipline PDFs, 176 pages) and checked by hand
against sheets already visually confirmed earlier:

- `classify_sheets.py` correctly identified: column schedule (Struct p3),
  foundation plan + pier cap schedule (Struct p7), framing plan (Struct
  p15), first floor plan (Arch p16), roof plan (Arch p22), building
  section (Arch p34), door schedule (Arch p43), window schedule (Arch
  p44), and both discipline sheet-index/cover pages (Civil p1, Struct p1).
- `extract_code_summary.py` pulled **77,315 SF gross building area, 36
  units, 6 stories** off the GEN sheet — matching exactly what we
  extracted by hand in the Nueces estimate, each with a citation.
- Its cross-check (sum of the 6 per-floor areas vs. the stated total)
  **passed exactly**: 14,208 + 14,171 + 13,164 + 11,924 + 11,924 + 11,924 =
  77,315. This is the first real, working example of the Phase 2 principle
  from `ESTIMATING_TEAM_PLAN.md`: never trust one source when a second
  exists — here, both agree, so both are now more trustworthy than
  either alone. A mismatch would have been flagged, not resolved silently.

## Lesson learned counting repeated plan callouts (2026-09-14)

Tried to count pier cap symbols (PC1-PC5) on the Nueces foundation plan by
cropping the sheet into quadrants and reading each visually. That method
turned out unreliable on its own — crop boundaries risk double-counting
or missing a symbol split across two images, and it nearly produced a
false-confident wrong total.

**Better method, proven on the same real page**: since these callouts are
real text in a CAD-exported PDF (not raster), count text occurrences of
each mark instead (`grep -oE "\bPC[1-5]\b" | sort | uniq -c` on
`pdftotext -layout` output), then subtract 1 per mark for its schedule-
table row. This matched the vision count exactly on 4 of 5 marks, and
where the fifth (PC3) disagreed (3 vs 4), checking a second sheet
(the same building's other foundation-plan page) confirmed the text
method's miss, not the vision count's error. **Rule going forward:
prefer text-occurrence counting over vision-cropping for any repeated
plan callout, and use vision counting only as the cross-check, not the
primary source** — the reverse of what felt intuitive to try first.

A real, honest gap came out of this too: PC1 appears in the schedule but
was never found as a plan callout on any of the three sheets classified
as `foundation_plan` in this set. Not resolved, not guessed at — flagged
as needing a human to check the source file directly.

## Lesson learned: trust the render, not just the regex (2026-09-15)

`extract_door_schedule.py`'s first version reported 54 doors and looked
clean — no errors, no obviously malformed rows. It was wrong. Rendering
the same page as an image and counting rows by eye (the same VISION RULE
cross-check used elsewhere) found 92-93 real rows, not 54. Two silent
bugs caused the gap: the location pattern didn't allow a hyphen, so every
"MULTI-PURPOSE" door (6 of them) failed to match with no error raised;
and a legend label sitting on the same text line as a real row (a layout-
bleed artifact, same root cause as the pier-cap page) got swallowed into
the door ID, mislabeling a real row instead of skipping it. Neither bug
would have been caught by re-reading the script or the JSON output alone
— both looked structurally fine. **The fix that actually caught this was
rendering the page and counting real rows against the tool's output
before trusting either one.** The corrected extractor also surfaced a
real data-quality issue in the source drawing itself (door ID `X102`
used twice, for two different rooms) — reported as found, not silently
deduplicated, per the same "flag anomalies, don't resolve them
silently" rule as the OCG issue below.

A second, separate real finding on the same sheet: a schedule titled
"WINDOW SCHEDULE" turned out, on inspection, to be a storefront
**elevation detail sheet** (dimensioned drawings of window/storefront
types with `EQ` spacing strings), not a row-based table — genuinely not
extractable as clean quantities via text, the same category of honest
gap as REScheck's two unhandled envelope-table layouts. Not forced.

## Known limitation — not solved, documented on purpose

Some pages contain text from **hidden/invisible CAD layers** that
`pdftotext` extracts regardless of visibility (seen as `Syntax Error:
Marked Content 'ocNN' is unknown` warnings on stderr — an Optional
Content Group the PDF viewer would hide, but the text layer doesn't). This
can make a page falsely match several sheet types at once (e.g. Civil p10
in the Nueces set). `classify_sheets.py` does **not** try to silently
resolve this — it reports all matched types as-is on pages beyond the
first 2, which is a real "this page touches many topics, a human/agent
should open and confirm" signal rather than a false single-type label.
Properly fixing this needs an OCG-aware PDF parser (not attempted here).
An index-page heuristic (page ≤2 with ≥4 matches → flagged as
`possible_sheet_index_or_toc`) is deliberately restricted to the first 2
pages of a discipline PDF, because applying it document-wide produced a
false negative on a real, high-value sheet (a first floor plan whose own
general notes legitimately reference many other sheet types).
