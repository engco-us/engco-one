# Context for ChatGPT — Round 2: more real examples, same 3 document types

## What changed since round 1
Round 1 found 6 candidate document families. We built and tested extractors for the top 3: COMcheck, REScheck, and TxDOT Estimate & Quantity sheets. All 3 work on the small samples tested. Now we need **depth, not breadth** — more real examples of these same 3 types, to get real statistical confidence (target: under 3% error) instead of a 3-5-document coincidence.

## What we already have (don't re-find these)
- **COMcheck** (5 docs): 2 from a real Huntsville, TX warehouse project; 1 Idaho DOT maintenance shed; 1 Utah DFCM office building; 1 residential/office at "2215 Silverway Drive."
- **REScheck** (5 docs): Pearland TX, a Colorado sample, a Pennsylvania sample, a 2021 IECC sample, a Wisconsin 2009 sample.
- **TxDOT E&Q** (3 projects): Martin, Bexar, and Hood counties.

## The ask
Find **10-15 more real, independent, directly-downloadable PDF examples of each of these 3 types** — different projects, different states/counties where relevant, not the same source republished.

1. **COMcheck Envelope Compliance Certificates** — any building type, any state.
2. **REScheck Compliance Certificates** — specifically useful: we found **3 different real envelope-assembly table layouts** across just 5 documents (a 2-column U-Factor/UA version, a 4-column Proposed+Required version, and an older-format report with a different section heading entirely). More examples showing which layout goes with which REScheck software version would help us close that gap — if you can note the software version number shown on each certificate you find, that's a bonus.
3. **TxDOT Estimate & Quantity sheets** — from `ftp.txdot.gov/plans/State-Let-Construction/`, different counties/years than Martin, Bexar, Hood.

## What makes a document extra valuable
A document where the target value (conditioned floor area, bid quantity, etc.) is **also independently stated somewhere else** — a filename, a project summary, a second sheet in the same set — the way "COMcheck-warehouse 1 (12000 ft2).pdf" let us confirm our extractor against the filename itself, or a web page's own summary text stating a number we could check the PDF against before writing any code. Flag these specifically if you find them — they're worth more than a plain document with no independent check.

## What's NOT needed
Same as round 1: no extraction code, no pricing/cost data, no new document families — this round is deliberately narrower, just more real examples of the 3 we've already proven work.
