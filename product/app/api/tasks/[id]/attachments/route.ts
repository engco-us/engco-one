import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { NextResponse } from 'next/server';
import { getProjects } from '@/lib/engco/data';
import { addTaskAttachment, getTask } from '@/lib/engco/tasks';

export const runtime = 'nodejs';

const maxBytes = 50 * 1024 * 1024;

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id: taskId } = await params;
  const task = await getTask(taskId);
  if (!task) return NextResponse.json({ error: 'Task not found.' }, { status: 404 });

  const form = await request.formData();
  const file = form.get('file');
  if (!(file instanceof File)) return NextResponse.json({ error: 'Choose a PDF file.' }, { status: 400 });
  if (file.size === 0 || file.size > maxBytes) return NextResponse.json({ error: 'PDF must be between 1 byte and 50 MB.' }, { status: 400 });

  const bytes = Buffer.from(await file.arrayBuffer());
  if (file.type !== 'application/pdf' || bytes.subarray(0, 5).toString() !== '%PDF-') {
    return NextResponse.json({ error: 'Only valid PDF files are accepted in this workflow.' }, { status: 415 });
  }

  const project = (await getProjects()).find((candidate) => candidate.project_id === task.projectId);
  if (!project) return NextResponse.json({ error: 'The task project no longer exists.' }, { status: 409 });

  const attachmentId = randomUUID();
  const safeName = path.basename(file.name).replace(/[^A-Za-z0-9._ -]/g, '_');
  const relativePath = path.join(project.folder, '00 - Project Control', 'ENGCO ONE Uploads', taskId, `${attachmentId}-${safeName}`);
  const absolutePath = path.resolve(process.cwd(), '..', relativePath);
  const projectRoot = path.resolve(process.cwd(), '..', project.folder);
  if (!absolutePath.startsWith(`${projectRoot}${path.sep}`)) return NextResponse.json({ error: 'Invalid storage path.' }, { status: 400 });

  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, bytes, { flag: 'wx' });
  const attachment = { id: attachmentId, name: safeName, size: file.size, mimeType: file.type, relativePath, uploadedAt: new Date().toISOString() };
  await addTaskAttachment(taskId, attachment);
  return NextResponse.json(attachment, { status: 201 });
}
