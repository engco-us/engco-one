#!/usr/bin/env python3
"""engco — one command for the whole system. Every tool is declared once
in cli/registry.py; this file only routes to it and prints help — it
never hardcodes a tool's argument shape, so the registry can't drift out
of sync with --help text.

Usage:
  engco                          list everything registered
  engco <category>               list commands in one category
  engco <category> <name> [...]  run a command, passing args straight through
  engco agents                   show the real agent registry
  engco sops                     show the real SOP backlog
  engco projects                 show the real project registry
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import COMMANDS, DATA_VIEWS  # noqa: E402


def categories():
    cats = {}
    for cmd in COMMANDS:
        cats.setdefault(cmd["category"], []).append(cmd)
    return cats


def print_all_help():
    print("engco — ENGCO ONE command line\n")
    cats = categories()
    for cat in sorted(cats):
        print(f"  {cat}")
        for cmd in cats[cat]:
            print(f"    engco {cat} {cmd['name']:<16} {cmd['help']}")
        print()
    print("  registries (real data, not a wrapped script)")
    for view in DATA_VIEWS:
        print(f"    engco {view['category']:<10}              {view['help']}")
    print("\nRun `engco <category>` to see just that group with full usage.")


def print_category_help(cat: str):
    cmds = [c for c in COMMANDS if c["category"] == cat]
    view = next((v for v in DATA_VIEWS if v["category"] == cat), None)
    if not cmds and not view:
        print(f"FAIL: unknown category {cat!r}. Run `engco` to see everything registered.")
        sys.exit(1)
    if view:
        print(f"engco {cat} — {view['help']}")
        return
    print(f"engco {cat} <name> [...args]\n")
    for cmd in cmds:
        print(f"  {cmd['name']:<16} {cmd['help']}")
        print(f"    usage: engco {cat} {cmd['name']} {cmd['usage']}\n")


def show_data_view(view: dict):
    path = ROOT / view["data_file"]
    if not path.exists():
        print(f"FAIL: {path} not found")
        sys.exit(1)
    data = json.loads(path.read_text())

    if view["category"] == "agents":
        for a in data["agents"]:
            owns = ", ".join(a.get("owns_functions", []))
            print(f"[{a['id']}] {a['name']:<32} status={a['status']:<6} owner={a['accountable_owner']}")
            if owns:
                print(f"       owns: {owns}")
        if data.get("unowned_functions"):
            print("\nUnassigned (human-only, no agent):")
            for u in data["unowned_functions"]:
                print(f"  - {u['function']}")
        return

    if view["category"] == "sops":
        for s in data["sops"]:
            owner = s.get("owner_name", s["owner_role"])
            print(f"[{s['id']}] {s['status']:<10} {s['priority']:<7} {s['procedure']} (owner: {owner})")
        return

    if view["category"] == "projects":
        for p in data["projects"]:
            print(f"[{p['project_id']}] {p['project_name']} — {p['current_phase']} / {p['overall_status']} "
                  f"(PM: {p['project_manager'] or 'TBD'})")
        return


def main():
    args = sys.argv[1:]

    if not args:
        print_all_help()
        return

    cat = args[0]

    view = next((v for v in DATA_VIEWS if v["category"] == cat), None)
    if view and len(args) == 1:
        show_data_view(view)
        return

    if len(args) == 1:
        print_category_help(cat)
        return

    name = args[1]
    rest = args[2:]
    cmd = next((c for c in COMMANDS if c["category"] == cat and c["name"] == name), None)
    if cmd is None:
        print(f"FAIL: no command registered as `engco {cat} {name}`. Run `engco {cat}` to see what's there.")
        sys.exit(1)

    script_path = ROOT / cmd["script"]
    subprocess.run(["python3", str(script_path)] + rest)


if __name__ == "__main__":
    main()
