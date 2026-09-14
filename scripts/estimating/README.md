# Estimating Toolkit

Phase 1 of `ESTIMATING_TEAM_PLAN.md`: deterministic tools that do the parts
of a takeoff that don't need judgment, so an agent never has to re-derive
them from scratch (and never has a chance to invent them).

## Tools

**`classify_sheets.py`** — scans every page of a discipline PDF and tags
its sheet type (floor plan, schedule, framing plan, code summary, etc.) by
keyword match. No model call, no cost, no invention risk.

**`extract_code_summary.py`** — pulls known code-summary fields (gross
building SF, unit count, stories, per-floor areas) off a general/cover
sheet, with an exact citation for every value — and runs a real
cross-check: do the per-floor areas actually sum to the stated total?
Uses `pdftotext -layout` (preserves column position), which was necessary:
plain-mode text interleaves multiple tables unpredictably when the same
label ("FIRST FLOOR:") appears in two different tables on one sheet.

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
