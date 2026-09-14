# Context for ChatGPT — ENGCO Estimating Toolkit research help

## What this is
ENGCO (a Texas engineering/construction/land-development firm) is building its own tool for reading construction plans and pulling out accurate quantities (square footage, bid-item counts, material amounts, etc.) — not an AI that "reads a PDF and guesses," but small, purpose-built tools, one per **standardized document type**, that extract numbers with zero tolerance for invented data.

## The core rule
Every extracted number must trace back to an exact source (file + page + the literal text it came from). If a tool can't find a real number, it must say "not found" — never guess or estimate in its place. This only works reliably for **standardized document formats** — ones with a consistent, predictable layout used across many different projects/architects/agencies — because a generic "read anything" approach can't be trusted not to invent things.

## What's built and proven so far (real documents, not samples)
- **COMcheck Envelope Compliance Certificate** (a DOE-published, nationally standardized energy-code form) — extracts building floor area + envelope assembly areas (roof, walls, doors, windows). Tested on 5 real independent documents from different states/projects; floor area matched known-correct values exactly on the one case with independent verification.
- **TxDOT Estimate & Quantity Sheet** (Texas DOT's standardized bid-item quantity table, present on every state highway letting) — extracts bid code, description, unit, quantity. Tested on 3 independent real TxDOT projects (different counties), 213 total bid items extracted. Found that TxDOT actually uses **two different real formats** for this (a 3-digit-code EST+FINAL version, and a 4-digit-code single-QTY "Quantity Summary" version) — the tool now handles both, found by testing against enough real documents to hit the second format.
- A building-code "code summary" extractor (gross SF, unit count, stories) — works well but is narrow, tied to one architect's specific label wording, doesn't generalize broadly yet.

## The actual current bottleneck
Finding **more real, independently-sourced documents of standardized types** to test against, so we can prove (or break and then fix) each tool at real scale — the goal is under 3% error, zero invented quantities, across many real documents, not just one or two.

## What would help
Research help finding:
1. **More standardized U.S. construction/engineering document types** we haven't targeted yet — ones with a consistent, predictable layout used industry-wide or by a government agency (examples of the *category* we're after: energy code compliance certificates, DOT bid-item quantity sheets, FEMA/flood forms, ADA compliance checklists, fire-marshal permit forms, utility company service-application forms — anything with a fixed, repeatable layout across many different projects).
2. **Real, publicly downloadable example documents** of each type — ideally direct PDF links from government agencies, universities, or other legitimate public sources, not paywalled or login-gated.
3. Bonus: any of these document types where a **second, independent source of the same number** exists in the same document set (so results can be cross-checked against each other, not just trusted blindly) — this is how we caught real extraction bugs earlier.

## What's NOT needed
- No help with the extraction code itself (that's built and tested here).
- No cost/pricing data — the current focus is quantities only, not dollar estimates.
- No AI-model recommendations or fine-tuning advice — this deliberately uses simple, deterministic scripts, not a trained model, so every rule stays inspectable and editable.
