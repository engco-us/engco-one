import { NextResponse } from 'next/server';
import { getTask } from '@/lib/engco/tasks';
import { saveTaskAttachment } from '@/lib/engco/attachments';

export const runtime = 'nodejs';

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id: taskId } = await params;
  const task = await getTask(taskId);
  if (!task) return NextResponse.json({ error: 'Task not found.' }, { status: 404 });

  const form = await request.formData();
  const file = form.get('file');
  if (!(file instanceof File)) return NextResponse.json({ error: 'Choose a PDF file.' }, { status: 400 });

  const result = await saveTaskAttachment(taskId, task.projectId, file);
  if ('error' in result) return NextResponse.json({ error: result.error }, { status: result.status });
  return NextResponse.json(result, { status: 201 });
}
