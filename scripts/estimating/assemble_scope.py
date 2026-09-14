#!/usr/bin/env python3
"""Assemble extracted quantities into one structured scope-of-work document.

This is the enforcement point for the plan's hard rule: every line item
MUST carry a source citation and a confidence label, or the whole
assembly fails loudly rather than shipping an incomplete line silently.

Confidence labels, most to least trustworthy:
  schedule_verified  - read directly from a real schedule/table, no math
  cross_checked      - two independent sources agree (see extract_code_summary.py)
  single_source      - one clean text extraction, not independently confirmed
  vision_count       - counted/identified visually, not from a table
  benchmark_only      - priced/estimated from a general benchmark, not the model
  unresolved         - a known gap; quantity intentionally left blank, not guessed

Usage: import build_line() and assemble() from another script, or run this
file directly to (re)build the real Nueces scope from the extraction
results already committed in this repo.
"""
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

VALID_CONFIDENCE = {
    "schedule_verified", "cross_checked", "single_source",
    "vision_count", "benchmark_only", "unresolved",
}


@dataclass
class Citation:
    source_file: str
    source_page: int
    source_snippet: str = ""


@dataclass
class ScopeLine:
    csi_division: str
    csi_division_name: str
    item: str
    quantity: Optional[float]
    unit: str
    confidence: str
    citations: list  # list[Citation]
    note: str = ""
    unit_rate: Optional[float] = None
    rate_source: Optional[str] = None  # "benchmark" | "vendor" | None
    total: Optional[float] = None

    def validate(self):
        errors = []
        if self.confidence not in VALID_CONFIDENCE:
            errors.append(f"invalid confidence {self.confidence!r}")
        if self.confidence != "unresolved":
            if not self.citations:
                errors.append("missing citation (required unless confidence='unresolved')")
            if self.quantity is None:
                errors.append("missing quantity (required unless confidence='unresolved')")
        if self.unit_rate is not None and self.rate_source is None:
            errors.append("unit_rate given without rate_source ('benchmark' or 'vendor')")
        return errors


def build_line(**kwargs) -> ScopeLine:
    line = ScopeLine(**kwargs)
    if line.unit_rate is not None and line.quantity is not None:
        line.total = round(line.unit_rate * line.quantity, 2)
    return line


def assemble(project_name: str, lines: list) -> dict:
    all_errors = []
    for i, line in enumerate(lines):
        errs = line.validate()
        if errs:
            all_errors.append((i, line.item, errs))
    if all_errors:
        msg = "\n".join(f"  line {i} ({item!r}): {errs}" for i, item, errs in all_errors)
        raise ValueError(f"Scope assembly FAILED — {len(all_errors)} line(s) invalid:\n{msg}")

    return {
        "project_name": project_name,
        "line_count": len(lines),
        "lines": [
            {**asdict(l), "citations": [asdict(c) if isinstance(c, Citation) else c for c in l.citations]}
            for l in lines
        ],
    }


def to_markdown(scope: dict) -> str:
    out = [f"# Scope of Work — {scope['project_name']}", ""]
    out.append("| Div | Item | Qty | Unit | Confidence | Rate | Total | Source |")
    out.append("|---|---|---|---|---|---|---|---|")
    for l in scope["lines"]:
        qty = f"{l['quantity']:,}" if l["quantity"] is not None else "—"
        rate = f"${l['unit_rate']:,}" if l.get("unit_rate") is not None else "—"
        total = f"${l['total']:,}" if l.get("total") is not None else "—"
        cites = "; ".join(f"{c['source_file'].split('/')[-1]} p{c['source_page']}" for c in l["citations"]) or "n/a (unresolved)"
        out.append(f"| {l['csi_division']} | {l['item']} | {qty} | {l['unit']} | {l['confidence']} | {rate} | {total} | {cites} |")
        if l.get("note"):
            out.append(f"| | *{l['note']}* | | | | | | |")
    return "\n".join(out)


if __name__ == "__main__":
    print(__doc__)
