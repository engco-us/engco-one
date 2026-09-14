#!/usr/bin/env python3
"""Common normalized lead record every connector must produce, per
docs/leads_finder_data_access_research.md's build recommendation. One
schema regardless of source, so downstream dedup/reporting doesn't need
to know which connector a lead came from.

Report-only by design: nothing in this schema or the connectors that
produce it sends anything anywhere. See scripts/leads/run_leads_report.py.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Lead:
    source: str  # "ESBD" | "SAM.gov"
    solicitation_id: str
    title: str
    agency: str
    posted_date: Optional[str]
    due_date: Optional[str]
    due_time: Optional[str]
    status: str
    codes: str  # NIGP / NAICS / PSC, whatever the source provides, as a plain string
    detail_url: str
    attachment_links: list
    first_seen: str  # ISO timestamp, set by the aggregator on first sighting
    last_checked: str  # ISO timestamp, updated every run
    source_evidence: dict  # the exact raw record from the source, unmodified — never summarized away

    def dedup_key(self) -> str:
        # Explicit per the build instructions: dedupe by source + solicitation ID, nothing fuzzier.
        return f"{self.source}:{self.solicitation_id}"

    def to_dict(self) -> dict:
        return asdict(self)
