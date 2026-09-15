# ENGCO ONE Product

The real, employee-facing app for ENGCO ONE — not an informative dashboard, a tool people use to get work done. Scaffolded from Vercel's MIT-licensed Next.js SaaS Starter, with the payments/marketing/multi-tenant parts stripped out: this is a single-company internal app, not something sold to other companies.

The primary surface is `/workspace`: pick a project, describe the outcome you need, get routed to the right governed agent (with its human owner and approval gate shown before you commit), and run it against real source documents. It reads the same `data/*.json` registries and calls the same `scripts/` as the Flask app in `../webapp` did — that app is being retired as this one gains parity.

## Local development

```bash
npm install
npm run db:setup      # creates .env — choose local Docker Postgres or point at a remote one
npm run db:migrate
npm run db:seed        # creates test@test.com / admin123
npm run dev
```

Open `http://localhost:3000/workspace`.

See `../PRODUCT_IMPLEMENTATION_PLAN.md` for scope, architecture, delivery slices, and the first-release definition.

## What's real right now

- `/workspace` — new-work composer, reads real `agent_registry.json` / `project_registry.json`.
- Agent recommendation (`lib/engco/workflows.ts`) — keyword-routes the outcome text to a real agent from the registry.
- Task creation (`lib/engco/tasks.ts`) — persists to `../data/tasks.json`. This is a stopgap; it does not handle concurrent writers safely and is slated to move into Postgres.
- Document upload + analysis (`lib/engco/analyze.ts`) — shells out to the real `scripts/estimating/classify_sheets.py`, same as the CLI and the Flask app do.
- Auth, teams, roles, activity log — the starter's scaffolding, present but not yet wired into `/workspace`.

## Tech stack

Next.js (App Router, TypeScript), Tailwind, shadcn/ui, Postgres + Drizzle ORM, JWT session cookies.
