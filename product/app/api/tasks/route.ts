import { NextResponse } from 'next/server';
import { getAgents, getProjects } from '@/lib/engco/data';
import { createTask } from '@/lib/engco/tasks';

export async function POST(request: Request) {
  const body = await request.json() as { outcome?: string; projectId?: string; agentId?: string };
  const outcome = body.outcome?.trim();
  if (!outcome || !body.projectId || !body.agentId) {
    return NextResponse.json({ error: 'Outcome, project, and agent are required.' }, { status: 400 });
  }

  const [projects, agents] = await Promise.all([getProjects(), getAgents()]);
  const project = projects.find((candidate) => candidate.project_id === body.projectId);
  const agent = agents.find((candidate) => candidate.id === body.agentId);
  if (!project || !agent) return NextResponse.json({ error: 'Project or agent was not found.' }, { status: 404 });

  const task = await createTask({
    outcome,
    projectId: project.project_id,
    projectName: project.project_name,
    agentId: agent.id,
    agentName: agent.name
  });
  return NextResponse.json(task, { status: 201 });
}
