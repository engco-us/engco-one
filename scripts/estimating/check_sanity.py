#!/usr/bin/env python3
"""Flag an extracted quantity as implausible if it falls outside a typical
range for its category — a cheap check that catches both extraction bugs
(wrong units, misread digit) and genuine anomalies worth a second look.

This does NOT prove a value is correct — being in-range is not a pass,
it's just "not an obvious red flag." Being out-of-range is not a fail
either — it's "a human should look at this before it's trusted," per
data/sanity_ranges.json's own stated purpose. Never auto-corrects a value.

Usage:
  python3 check_sanity.py --category structural_steel_framing --numerator 620000 --numerator-unit kg --denominator 77315 --denominator-unit sf
  python3 check_sanity.py --list   # show all known categories and their ranges
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RANGES_PATH = ROOT / "data" / "sanity_ranges.json"

KG_TO_LB = 2.20462


def load_ranges():
    return json.loads(RANGES_PATH.read_text())["ranges"]


def find_category(name, ranges):
    return next((r for r in ranges if r["category"] == name), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", help="One of the categories in data/sanity_ranges.json")
    ap.add_argument("--numerator", type=float, help="e.g. total steel quantity")
    ap.add_argument("--numerator-unit", default=None, help="kg or lb (auto-converts to lb for steel checks)")
    ap.add_argument("--denominator", type=float, help="e.g. gross SF")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    ranges = load_ranges()

    if args.list:
        for r in ranges:
            print(f"[{r['category']}] {r['low']}-{r['high']} {r['unit']}")
            print(f"    {r['note']}")
        return

    if not (args.category and args.numerator is not None and args.denominator):
        print("FAIL: --category, --numerator, and --denominator are required (or use --list)")
        return

    r = find_category(args.category, ranges)
    if r is None:
        print(f"FAIL: unknown category {args.category!r}. Use --list to see known categories.")
        return

    numerator = args.numerator
    if args.numerator_unit == "kg" and "lb" in r["unit"]:
        numerator = numerator * KG_TO_LB

    ratio = numerator / args.denominator
    in_range = r["low"] <= ratio <= r["high"]

    print(f"category: {r['category']}")
    print(f"ratio: {ratio:.4f} {r['unit']} (typical range: {r['low']}-{r['high']})")
    print(f"note: {r['note']}")
    if in_range:
        print("RESULT: within typical range — not an obvious red flag (not proof of correctness)")
    else:
        print("RESULT: OUTSIDE typical range — FLAG FOR HUMAN REVIEW (not necessarily wrong — check context, e.g. mixed-use program, deep foundations, reduced-parking overlay)")


if __name__ == "__main__":
    main()
