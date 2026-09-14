#!/usr/bin/env python3
"""Extract building area and envelope assembly areas from a COMcheck
Envelope Compliance Certificate. COMcheck is a DOE-published, nationally
standardized energy-code compliance form — unlike extract_code_summary.py
(built around one architect's specific label wording), this should
generalize to ANY COMcheck report, from any project, any state.

Refuses to guess: if the expected table isn't found, reports not_found
rather than inventing a number.

Usage:
  python3 extract_comcheck.py "COMcheck-warehouse 1 (12000 ft2).pdf"
"""
import argparse
import json
import re
import subprocess


def get_text(pdf_path: str) -> str:
    result = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True)
    return result.stdout


def extract(text: str, pdf_path: str) -> dict:
    lines = text.splitlines()
    out = {"project_title": None, "climate_zone": None, "floor_area_sf": None,
           "envelope_assemblies": [], "citations_file": pdf_path}

    for line in lines:
        m = re.search(r"Project Title:\s*(.+?)\s*$", line)
        if m:
            out["project_title"] = m.group(1).strip()
        m = re.search(r"Climate Zone:\s*(\S+)", line)
        if m:
            out["climate_zone"] = m.group(1).strip()

    # Floor Area sits under a "Building Area ... Floor Area" header, on the
    # next non-blank line, as: "<use label> : <occupancy>   <number>"
    for i, line in enumerate(lines):
        if "Building Area" in line and "Floor Area" in line:
            for j in range(i + 1, min(i + 5, len(lines))):
                m = re.search(r":\s*\S.*?(\d[\d,]*)\s*$", lines[j])
                if m:
                    out["floor_area_sf"] = int(m.group(1).replace(",", ""))
                    out["floor_area_source_line"] = lines[j].strip()
                    break
            break

    # Envelope assemblies: "<Assembly description ...>   <Gross Area>  <other columns...>"
    # Gross Area is the first number after the description text on these rows.
    in_table = False
    for line in lines:
        if "Envelope Assemblies" in line:
            in_table = True
            continue
        if not in_table:
            continue
        head = re.match(r"^(Floor|Roof|Ext\. Wall|Door|Window|Skylight)[:\s]", line)
        if head:
            # Two earlier approaches both failed on real data: anchoring on
            # the closing "]" of "[Bldg. Use N - Type]" fails when that tag
            # wraps onto a second physical line; a fixed column offset fails
            # because it can start mid-word. What's actually reliable: the
            # Gross Area cell is always immediately followed by "---" (the
            # blank Cavity/Cont. R-Value cells) in every real row, so anchor
            # on that instead of position or bracket-matching.
            m = re.search(r"(\d[\d,]*)\s+---", line)
            if m:
                out["envelope_assemblies"].append({
                    "assembly_type": head.group(1),
                    "gross_area_sf": int(m.group(1).replace(",", "")),
                    "source_line": line.strip()[:160],
                })
        if "Compliance Statement" in line or "Inspection Checklist" in line:
            break

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    args = ap.parse_args()

    text = get_text(args.pdf)
    result = extract(text, args.pdf)
    print(json.dumps(result, indent=2))
    if result["floor_area_sf"] is None:
        print("\nFLOOR AREA NOT FOUND — reported honestly, not guessed. "
              "This PDF may not be a COMcheck Envelope Compliance Certificate, "
              "or its layout differs from what this tool expects.")


if __name__ == "__main__":
    main()
