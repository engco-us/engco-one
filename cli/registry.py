"""The one place every command in this system is registered. Adding a new
tool means adding one entry here — never editing a big if/elif dispatcher.
`engco` (the CLI in cli/engco.py) reads this list to route commands and to
generate its own --help text, so the registry and the help text can never
drift apart.
"""

COMMANDS = [
    # --- estimating toolkit ---
    {"category": "estimate", "name": "classify", "script": "scripts/estimating/classify_sheets.py",
     "help": "Tag every page of a PDF by sheet type (floor plan, schedule, etc.)",
     "usage": "<pdf> [--discipline NAME] [--out manifest.json]"},
    {"category": "estimate", "name": "code-summary", "script": "scripts/estimating/extract_code_summary.py",
     "help": "Pull gross SF / unit count / stories / floor areas off a code summary sheet",
     "usage": "<pdf> --page N"},
    {"category": "estimate", "name": "comcheck", "script": "scripts/estimating/extract_comcheck.py",
     "help": "Pull floor area + envelope assemblies from a COMcheck certificate",
     "usage": "<pdf>"},
    {"category": "estimate", "name": "rescheck", "script": "scripts/estimating/extract_rescheck.py",
     "help": "Pull conditioned floor area from a REScheck certificate",
     "usage": "<pdf>"},
    {"category": "estimate", "name": "txdot", "script": "scripts/estimating/extract_txdot_eq.py",
     "help": "Pull bid items from a TxDOT Estimate & Quantity sheet",
     "usage": "<pdf> --page N   (or --find-pages to locate it first)"},
    {"category": "estimate", "name": "render", "script": "scripts/estimating/render_sheet.py",
     "help": "Render one PDF page to an image, for vision reading",
     "usage": "<pdf> <page> --out path"},
    {"category": "estimate", "name": "sanity-check", "script": "scripts/estimating/check_sanity.py",
     "help": "Flag an implausible quantity against benchmark ranges",
     "usage": "--category NAME --numerator N --denominator N   (or --list)"},
    {"category": "estimate", "name": "score", "script": "scripts/estimating/score_quantity_tests.py",
     "help": "Run the golden quantity test manifest, report real accuracy",
     "usage": "[--tolerance-pct N]"},
    {"category": "estimate", "name": "door-schedule", "script": "scripts/estimating/extract_door_schedule.py",
     "help": "Pull door ID/location/width/height off a door & frame schedule",
     "usage": "<pdf> --page N   (or --find-pages to locate it first)"},
    {"category": "estimate", "name": "hcfcd-detention", "script": "scripts/estimating/extract_hcfcd_detention.py",
     "help": "Pull the detention-basin summary table off a Harris County Flood Control District Review Sheet",
     "usage": "<pdf> --page N   (or --find-pages to locate it first)"},
    {"category": "estimate", "name": "auto", "script": "scripts/estimating/auto_extract.py",
     "help": "Try every proven extractor (COMcheck/REScheck/TxDOT/door schedule/HCFCD) and report only real matches",
     "usage": "<pdf>"},

    # --- design/engineering QA ---
    {"category": "qa", "name": "sheet-index", "script": "scripts/qa/check_sheet_index.py",
     "help": "Catch a missing/swapped/mislabeled sheet by cross-checking the cover index against every page's own stamp",
     "usage": "<pdf>"},

    # --- leads finder ---
    {"category": "leads", "name": "report", "script": "scripts/leads/run_leads_report.py",
     "help": "Run every lead connector, dedupe, flag construction-relevant leads",
     "usage": "[--days-back N] [--samgov]"},
    {"category": "leads", "name": "esbd", "script": "scripts/leads/fetch_esbd.py",
     "help": "Fetch TxDOT lettings from ESBD directly (no API key needed)",
     "usage": "[--days-back N] [--start MM/DD/YYYY --end MM/DD/YYYY]"},
    {"category": "leads", "name": "samgov", "script": "scripts/leads/fetch_samgov.py",
     "help": "Fetch federal opportunities from SAM.gov (needs SAM_GOV_API_KEY)",
     "usage": "[--days-back N] [--state XX]"},
    {"category": "leads", "name": "austin-permits", "script": "scripts/leads/fetch_austin_permits.py",
     "help": "Fetch real commercial building permits issued in Austin",
     "usage": "[--days-back N]"},

    # --- project / governance ---
    {"category": "project", "name": "new", "script": "scripts/new_project.py",
     "help": "Register a new project per SOP-001: folders + registry row",
     "usage": "--name X --city X --client X --type X"},
    {"category": "project", "name": "validate", "script": "scripts/validate_record.py",
     "help": "Validate a project registry row against required fields/vocab",
     "usage": "--project-id ENG-YYYY-### [--max-staleness-days N]"},

    {"category": "scorecard", "name": "add", "script": "scripts/scorecard.py",
     "help": "Log this week's scorecard numbers",
     "usage": "--add --week-of YYYY-MM-DD --active-projects N --proposals-out N --cash-position N --recorded-by NAME"},
    {"category": "scorecard", "name": "auto", "script": "scripts/scorecard_auto.py",
     "help": "Derive active_projects/proposals_out from the real project registry (only cash position stays manual)",
     "usage": "[--add --cash-position N --recorded-by NAME]"},
    {"category": "scorecard", "name": "check", "script": "scripts/scorecard.py",
     "help": "Check whether the scorecard is stale",
     "usage": "--check [--max-staleness-days N]"},
    {"category": "scorecard", "name": "latest", "script": "scripts/scorecard.py",
     "help": "Show the most recent scorecard entry",
     "usage": "--latest"},

    # --- agents ---
    {"category": "agent", "name": "eval", "script": "scripts/run_agent_eval.py",
     "help": "Print the required eval cases for an agent",
     "usage": "--agent A-0N"},
    {"category": "agent", "name": "log-run", "script": "scripts/log_agent_run.py",
     "help": "Log a real agent run and any reviewer correction",
     "usage": "--agent X --project X --task X --reviewer X [--correction X] [--promote-to-instructions]"},
    {"category": "agent", "name": "promote", "script": "scripts/promote_learning.py",
     "help": "Surface repeated corrections worth writing into an agent's instructions",
     "usage": "--list   (or --mark-promoted RUN-ID)"},
]

# Registries that aren't scripts to dispatch to — engco reads these files
# directly and prints them, so `engco agents` etc. always reflects the real
# data in data/*.json, not a copy that can drift out of sync with it.
DATA_VIEWS = [
    {"category": "agents", "name": "list", "data_file": "data/agent_registry.json",
     "help": "List all 7 registered agents, their status, and who owns them"},
    {"category": "sops", "name": "list", "data_file": "data/sop_backlog.json",
     "help": "List all SOPs and their status (Missing / Draft / Approved)"},
    {"category": "projects", "name": "list", "data_file": "data/project_registry.json",
     "help": "List all registered active projects"},
]
