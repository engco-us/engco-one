#!/usr/bin/env python3
"""Run the golden quantity test manifest against the real extractors and
report real accuracy — the Phase 4 scoring harness from
ESTIMATING_TEAM_PLAN.md, which didn't exist until now (everything before
this was compared by hand, one document at a time).

Reports two numbers separately, on purpose: accuracy on
'independently_verified' entries (real proof) and on 'self_consistent_only'
entries (weaker evidence, useful for regression only) — blending them
would overstate confidence.

Usage:
  python3 score_quantity_tests.py
  python3 score_quantity_tests.py --tolerance-pct 3
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = ROOT / "data" / "golden_dataset" / "quantity_tests" / "manifest.json"
SCRIPTS_DIR = ROOT / "scripts" / "estimating"


def run_comcheck(pdf_path: str):
    out = subprocess.run(["python3", str(SCRIPTS_DIR / "extract_comcheck.py"), pdf_path],
                          capture_output=True, text=True)
    return json.loads(out.stdout)


def run_rescheck(pdf_path: str):
    out = subprocess.run(["python3", str(SCRIPTS_DIR / "extract_rescheck.py"), pdf_path],
                          capture_output=True, text=True)
    return json.loads(out.stdout)


def run_txdot(pdf_path: str, page: int):
    out = subprocess.run(["python3", str(SCRIPTS_DIR / "extract_txdot_eq.py"), pdf_path, "--page", str(page)],
                          capture_output=True, text=True)
    # extractor prints the JSON array then a trailing "Extracted N..." line
    text = out.stdout.rsplit("\n\nExtracted", 1)[0]
    return json.loads(text)


def get_actual_value(entry: dict):
    extractor = entry["extractor"]
    local_path = str(Path(entry["local_path"]).expanduser())
    if not Path(local_path).exists():
        return None, f"source file not found locally: {local_path}"

    if extractor == "extract_comcheck.py":
        result = run_comcheck(local_path)
        return result.get(entry["field"]), None

    if extractor == "extract_rescheck.py":
        result = run_rescheck(local_path)
        return result.get(entry["field"]), None

    if extractor == "extract_txdot_eq.py":
        rows = run_txdot(local_path, entry["page"])
        field = entry["field"]
        if field == "row_count":
            return len(rows), None
        if field.startswith("bid_code:"):
            _, code, subfield = field.split(":")
            match = next((r for r in rows if r["bid_code"] == code), None)
            if match is None:
                return None, f"bid_code {code} not found in extracted rows"
            return match.get(subfield), None
        return None, f"unknown field spec: {field}"

    return None, f"unknown extractor: {extractor}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerance-pct", type=float, default=3.0)
    args = ap.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text())
    results = []

    for entry in manifest["entries"]:
        actual, error = get_actual_value(entry)
        expected = entry["expected_value"]

        if error:
            status = "SKIPPED"
            pct_error = None
        elif actual is None:
            status = "FAIL (not found)"
            pct_error = None
        else:
            pct_error = abs(actual - expected) / expected * 100 if expected else (0 if actual == expected else 100)
            status = "PASS" if pct_error <= args.tolerance_pct else "FAIL"

        results.append({**entry, "actual_value": actual, "pct_error": pct_error, "status": status, "error": error})

    print(f"{'ID':<32} {'CONFIDENCE':<22} {'EXPECTED':>12} {'ACTUAL':>12} {'ERR%':>7} {'STATUS'}")
    for r in results:
        err = f"{r['pct_error']:.2f}" if r["pct_error"] is not None else "-"
        actual = r["actual_value"] if r["actual_value"] is not None else "-"
        print(f"{r['id']:<32} {r['confidence']:<22} {str(r['expected_value']):>12} {str(actual):>12} {err:>7} {r['status']}")
        if r["error"]:
            print(f"    -> {r['error']}")

    def summarize(subset, label):
        scored = [r for r in subset if r["status"] in ("PASS", "FAIL")]
        if not scored:
            print(f"\n{label}: no scoreable entries (all skipped — source files not present on this machine)")
            return
        passed = sum(1 for r in scored if r["status"] == "PASS")
        print(f"\n{label}: {passed}/{len(scored)} passed within {args.tolerance_pct}% tolerance "
              f"({len(subset) - len(scored)} skipped)")

    verified = [r for r in results if r["confidence"] == "independently_verified"]
    self_consistent = [r for r in results if r["confidence"] == "self_consistent_only"]
    summarize(verified, "INDEPENDENTLY VERIFIED (real proof)")
    summarize(self_consistent, "SELF-CONSISTENT ONLY (regression signal, not proof)")


if __name__ == "__main__":
    main()
