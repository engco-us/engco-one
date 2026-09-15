import { NextResponse } from 'next/server';
import { getAgents, getProjects } from '@/lib/engco/data';
import { createTask } from '@/lib/engco/tasks';
import { saveTaskAttachment } from '@/lib/engco/attachments';
import { analyzeTaskDocuments } from '@/lib/engco/analyze';

export const runtime = 'nodejs';

// Collapses the whole "create a task, upload a plan set, run it through the
// estimating pipeline" flow into one request triggered by one file drop —
// no separate agent-recommendation round trip, since a PDF upload is
// unambiguously an estimating job (A-05), the one agent with real tooling
// behind document analysis today.
export async function POST(request: Request) {
  const form = await request.formData();
  const projectId = form.get('projectId');
  const file = form.get('file');
  if (typeof projectId !== 'string' || !projectId) return NextResponse.json({ error: 'Choose a project.' }, { status: 400 });
  if (!(file instanceof File)) return NextResponse.json({ error: 'Choose a PDF file.' }, { status: 400 });

  const [projects, agents] = await Promise.all([getProjects(), getAgents()]);
  const project = projects.find((p) => p.project_id === projectId);
  const agent = agents.find((a) => a.id === 'A-05');
  if (!project) return NextResponse.json({ error: 'Project not found.' }, { status: 404 });
  if (!agent) return NextResponse.json({ error: 'Estimating agent not found in the registry.' }, { status: 500 });

  const task = await createTask({
    outcome: `Quantity takeoff — ${file.name}`,
    projectId: project.project_id,
    projectName: project.project_name,
    agentId: agent.id,
    agentName: agent.name,
  });

  const saved = await saveTaskAttachment(task.id, project.project_id, file);
  if ('error' in saved) return NextResponse.json({ error: saved.error, taskId: task.id }, { status: saved.status });

  try {
    await analyzeTaskDocuments(task.id);
  } catch {
    // Task and upload still succeeded — land on the task page either way
    // and let the existing Analyze button retry, rather than losing the work.
  }

  return NextResponse.json({ taskId: task.id }, { status: 201 });
}
