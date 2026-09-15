# ENGCO ONE Product

The real, employee-facing app for ENGCO ONE — not an informative dashboard, a tool people use to get work done. Scaffolded from Vercel's MIT-licensed Next.js SaaS Starter, with the payments/marketing/multi-tenant parts stripped out: this is a single-company internal app, not something sold to other companies.

The primary surface is `/workspace`: pick a project, describe the outcome you need, get routed to the right governed agent (with its human owner and approval gate shown before you commit), and run it against real source documents. It reads the same `data/*.json` registries and calls the same `scripts/` as the Flask app in `../webapp` did — that app is being retired as this one gains parity.

## Local development

```bash
docker compose up -d   # starts local Postgres on 5432 (engco/engco/engco)
npm install
npm run db:migrate
npm run db:seed         # creates test@test.com / admin123 and the ENGCO team
npm run dev
```

Create a `.env` (gitignored) with at least:
```
POSTGRES_URL=postgres://engco:engco@127.0.0.1:5432/engco
BASE_URL=http://localhost:3000
AUTH_SECRET=<openssl rand -hex 32>
```
(`npm run db:setup` will generate this interactively instead, if you'd rather not hand-write it.)

Open `http://localhost:3000/workspace`.

See `../PRODUCT_IMPLEMENTATION_PLAN.md` for scope, architecture, delivery slices, and the first-release definition.

## What's real right now

- `/workspace` — new-work composer, reads real `agent_registry.json` / `project_registry.json`.
- Agent recommendation (`lib/engco/workflows.ts`) — keyword-routes the outcome text to a real agent from the registry.
- Task creation (`lib/engco/tasks.ts`) — persists to a real `tasks` table in Postgres. Attachment uploads append via an atomic `jsonb || jsonb` update rather than a read-modify-write, so two uploads landing at once can't clobber each other.
- Document upload + analysis (`lib/engco/analyze.ts`) — shells out to the real `scripts/estimating/classify_sheets.py`, same as the CLI and the Flask app do.
- Auth, teams, roles, activity log — the starter's scaffolding, present but not yet wired into `/workspace` (no login is required to create a task yet — that's next).

## Tech stack

Next.js (App Router, TypeScript), Tailwind, shadcn/ui, Postgres + Drizzle ORM, JWT session cookies.
