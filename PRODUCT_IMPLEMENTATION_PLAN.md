# ENGCO ONE Product Implementation Plan

## Product outcome

Turn ENGCO ONE into a professional, self-hosted operations workspace that another company can install on its own computer, open in a browser, and use to assign real project work to governed AI agents. The product must move work from request to evidence-backed deliverable and human approval; reporting supports that workflow rather than replacing it.

## Foundation: reuse before custom code

Start with Vercel's MIT-licensed Next.js SaaS Starter and retain its Next.js App Router, TypeScript, Tailwind, shadcn/ui primitives, authentication, teams, role controls, Drizzle/Postgres schema, protected routes, and activity log. Use shadcn blocks for navigation, forms, tables, dialogs, sheets, command menus, empty states, and responsive layout. Use established packages for uploads, validation, AI streaming, job processing, document preview, and notifications. Keep the existing Python project, scorecard, leads, and estimating scripts behind a typed worker/API adapter until replacing one is demonstrably worthwhile. Package Next.js in standalone mode with PostgreSQL and the worker in Docker Compose for one-command customer installation.

## Core workflow and information architecture

The primary flow is **New work -> choose project -> describe outcome -> attach evidence -> recommended agent -> run -> questions/approval -> deliverable -> audit history**. Navigation will be Home, Work, Projects, Agents, Approvals, Deliverables, Knowledge, and Settings. Home prioritizes assigned work, blocked runs, and approvals. A project owns tasks, source files, decisions, risks, agent runs, and deliverables. The Agents page launches a bounded capability and explains required inputs, expected outputs, human owner, and prohibited actions; it is not merely an agent directory.

## Product model

Postgres becomes the transactional source of truth for organizations, users, memberships, projects, tasks, task assignments, agent definitions, agent runs, messages, attachments, approval requests, decisions, deliverables, activity events, and reusable knowledge sources. Task states are Draft, Ready, Running, Needs information, Awaiting approval, Revision requested, Complete, Failed, and Cancelled. Every agent run records its input snapshot, model/runtime, tool activity, source evidence, output, errors, and accountable human. Customer files remain in a configurable local data volume. Existing JSON is imported once and remains available for rollback during migration.

## Delivery slices

1. **Foundation:** branded reusable application shell, local configuration, database/auth setup, Docker packaging, health checks, and JSON import.
2. **First usable loop:** create a task, select a project, recommend/confirm an agent, persist the task, display its timeline, ask for missing information, and complete a simulated run.
3. **Real execution:** worker queue, OpenAI provider configuration, streaming run events, tool adapters for existing Python scripts, retries, cancellation, and structured evidence.
4. **Governance:** approval inbox, role-aware decision gates, revisions, immutable activity log, agent boundaries, and exportable run history.
5. **Deliverables and files:** uploads, local storage, previews, generated artifacts, versioning, export/download, and project knowledge retrieval.
6. **Distribution:** Docker Compose installer, first-run administrator setup, backups/restores, upgrades/migrations, diagnostics, signed releases, and customer documentation.

## Definition of first release

A new customer can install ENGCO ONE, create its administrator and company, import or create a project, upload source files, request a concrete outcome, run the correct agent, answer questions, approve controlled decisions, and download a deliverable with a complete evidence and activity trail. No agent may send external communication, approve money/scope/schedule, or claim professional authority without an explicit configured human gate.

## Immediate implementation

The modern app lives in `product/`; the Flask app remains available during migration. The first implementation establishes the starter foundation, a responsive ENGCO operations shell, live read-only adapters for the current project/agent/SOP/scorecard registries, and a prominent New Work composer. Next, persist the composer to the new task schema and connect one agent workflow end to end before expanding the dashboard surface.
