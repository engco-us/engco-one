# Design / Engineering QA Toolkit

Deterministic checks that catch real, boring, expensive plan-set mistakes
before a human finds them by flipping through every page — backing **A-04**
in `data/agent_registry.json`.

## Tools

**`check_sheet_index.py`** — cross-checks a plan set's cover-sheet "SHEET
INDEX" (real text, read directly) against each page's own printed
self-identifying "current sheet / total sheets" stamp. Catches a missing
sheet, an extra sheet, or two sheets swapped out of order — real mistakes
that happen when a set gets reassembled.

## Validated against real data (2026-09-15)

Ran against the real ENG-2026-002 (Kingwood) water-line plan set (8 pages,
D+A Associates): correctly parsed all 8 real sheet-index rows and confirmed
all 8 pages self-identify correctly — a genuine clean bill of health, not
just "no errors thrown."

Then proved it actually catches a real mistake, not just passes everything:
built a test file with sheets 04 and 05 swapped (`pypdf`, reordering real
pages from the same PDF) and re-ran it — correctly flagged both pages by
exact page number with the real stamped-vs-expected values, and correctly
left every other page reporting clean.

## A real layout-bleed lesson (same root cause as the door schedule)

The cover sheet's index rows don't always sit alone on their own text line
— row 3 on the Kingwood cover sheet ("03  OVERALL SITE PLAN") shares a
`-layout` text line with an unrelated caption ("LOCATION MAP") from a
graphic positioned at the same vertical height, because `pdftotext -layout`
merges text by row position, not by what's visually grouped. The fix isn't
special-casing that one page: search each line for the row pattern with
`re.search` (not anchored to line start), then keep only matches that
continue the expected 01, 02, 03... sequence — that sequence check is what
actually rejects a stray unrelated match, not knowing this specific page's
quirks in advance.

## Known limitation — not solved, documented on purpose

The cover sheet itself doesn't carry the same numeric self-ID stamp as
every other page in this template (it carries the index instead), so it's
identified by definition rather than cross-checked. If a plan set's cover
sheet template also omits the sheet index (not tested), this tool has
nothing to check against and should be extended to report that honestly,
not assume the set is fine.
