#!/usr/bin/env python3
"""ENGCO ONE local web app — a clean front door to the same tools and data
already built in scripts/ and data/. Nothing here is a separate source of
truth: every page reads the real data/*.json files directly, and every
action button runs the real script in scripts/ — same as engco (the CLI)
does. Run: python3 webapp/app.py, then open http://127.0.0.1:5050
"""
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__)


def load(rel_path: str):
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text())


@app.route("/")
def dashboard():
    agents = load("data/agent_registry.json").get("agents", [])
    sops = load("data/sop_backlog.json").get("sops", [])
    projects = load("data/project_registry.json").get("projects", [])
    sc = load("data/scorecard.json").get("entries", [])

    latest = sc[-1] if sc else None
    stale = False
    if latest:
        age = (date.today() - date.fromisoformat(latest["week_of"])).days
        stale = age > 7

    missing_high = [s for s in sops if s["status"] == "Missing" and s["priority"] == "High"]

    return render_template(
        "dashboard.html", active="dashboard",
        agent_count=len(agents),
        live_agent_count=sum(1 for a in agents if a["status"] in ("Pilot", "Active")),
        sop_total=len(sops),
        sop_approved=sum(1 for s in sops if s["status"] == "Approved"),
        project_count=len(projects),
        scorecard=latest, stale=stale,
        missing_high_sops=missing_high[:8],
    )


@app.route("/agents")
def agents():
    data = load("data/agent_registry.json")
    return render_template("agents.html", active="agents",
                            agents=data.get("agents", []),
                            unowned=data.get("unowned_functions", []))


@app.route("/sops")
def sops():
    data = load("data/sop_backlog.json")
    return render_template("sops.html", active="sops", sops=data.get("sops", []))


@app.route("/projects")
def projects():
    data = load("data/project_registry.json")
    return render_template("projects.html", active="projects", projects=data.get("projects", []))


@app.route("/projects/new", methods=["POST"])
def new_project():
    args = ["python3", str(ROOT / "scripts" / "new_project.py"),
            "--name", request.form["name"], "--city", request.form["city"],
            "--client", request.form["client"], "--type", request.form["type"]]
    subprocess.run(args, cwd=ROOT)
    return redirect(url_for("projects"))


@app.route("/scorecard")
def scorecard():
    data = load("data/scorecard.json")
    return render_template("scorecard.html", active="scorecard", entries=data.get("entries", []))


@app.route("/scorecard/add", methods=["POST"])
def add_scorecard():
    f = request.form
    args = ["python3", str(ROOT / "scripts" / "scorecard.py"), "--add",
            "--week-of", f["week_of"], "--active-projects", f["active_projects"],
            "--proposals-out", f["proposals_out"], "--cash-position", f["cash_position"],
            "--recorded-by", f["recorded_by"]]
    if f.get("notes"):
        args += ["--notes", f["notes"]]
    subprocess.run(args, cwd=ROOT)
    return redirect(url_for("scorecard"))


@app.route("/leads")
def leads():
    return render_template("leads.html", active="leads", output=None)


@app.route("/leads/run", methods=["POST"])
def run_leads():
    days_back = request.form.get("days_back", "14")
    sources = request.form.getlist("source")
    output_parts = []

    if "esbd" in sources:
        r = subprocess.run(["python3", str(ROOT / "scripts" / "leads" / "fetch_esbd.py"),
                             "--days-back", days_back], capture_output=True, text=True, cwd=ROOT)
        output_parts.append(f"=== ESBD / TxDOT ===\n{r.stderr.strip()}\n")

    if "austin" in sources:
        r = subprocess.run(["python3", str(ROOT / "scripts" / "leads" / "fetch_austin_permits.py"),
                             "--days-back", days_back], capture_output=True, text=True, cwd=ROOT)
        tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()
        output_parts.append(f"=== Austin Permits ===\n{tail}\n")

    if "samgov" in sources:
        r = subprocess.run(["python3", str(ROOT / "scripts" / "leads" / "fetch_samgov.py"),
                             "--days-back", days_back], capture_output=True, text=True, cwd=ROOT)
        output_parts.append(f"=== SAM.gov ===\n{(r.stdout or r.stderr).strip()}\n")

    output = "\n".join(output_parts) or "No sources selected."
    return render_template("leads.html", active="leads", output=output)


if __name__ == "__main__":
    port = 5050
    print(f"ENGCO ONE running at http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
