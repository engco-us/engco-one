import 'server-only';

import { readFile } from 'node:fs/promises';
import path from 'node:path';

export type Agent = {
  id: string;
  name: string;
  mission: string;
  status: string;
  accountable_owner: string;
  hard_boundaries: string;
  approval_gate: string;
  owns_functions?: string[];
};
export type Project = { project_id: string; project_name: string; city: string; current_phase: string; overall_status: string; folder: string };
type Sop = { status: string; priority: string };
type ScorecardEntry = { week_of: string; active_projects: number; proposals_out: number; cash_position: number };

async function readJson<T>(file: string): Promise<T> {
  const dataRoot = path.resolve(process.cwd(), '..', 'data');
  return JSON.parse(await readFile(path.join(dataRoot, file), 'utf8')) as T;
}

export async function getAgents() {
  return (await readJson<{ agents: Agent[] }>('agent_registry.json')).agents;
}

export type UnownedFunction = { function: string; status: string; note: string };

export async function getAgentRegistry() {
  return readJson<{ agents: Agent[]; unowned_functions?: UnownedFunction[] }>('agent_registry.json');
}

export async function getProjects() {
  return (await readJson<{ projects: Project[] }>('project_registry.json')).projects;
}

export async function getWorkspaceSnapshot() {
  const [agentRegistry, projectRegistry, sopBacklog, scorecard] = await Promise.all([
    readJson<{ agents: Agent[] }>('agent_registry.json'),
    readJson<{ projects: Project[] }>('project_registry.json'),
    readJson<{ sops: Sop[] }>('sop_backlog.json'),
    readJson<{ entries: ScorecardEntry[] }>('scorecard.json')
  ]);

  return {
    agents: agentRegistry.agents,
    projects: projectRegistry.projects,
    sops: sopBacklog.sops,
    latestScorecard: scorecard.entries.at(-1) ?? null
  };
}
