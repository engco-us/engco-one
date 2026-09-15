import 'server-only';

import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { getProjects, type Project } from './data';
import { addTaskAttachment, type TaskAttachment } from './tasks';

const maxBytes = 50 * 1024 * 1024;

export async function saveTaskAttachment(taskId: string, projectId: string, file: File): Promise<TaskAttachment | { error: string; status: number }> {
  if (file.size === 0 || file.size > maxBytes) return { error: 'PDF must be between 1 byte and 50 MB.', status: 400 };

  const bytes = Buffer.from(await file.arrayBuffer());
  if (file.type !== 'application/pdf' || bytes.subarray(0, 5).toString() !== '%PDF-') {
    return { error: 'Only valid PDF files are accepted in this workflow.', status: 415 };
  }

  const project = (await getProjects()).find((candidate: Project) => candidate.project_id === projectId);
  if (!project) return { error: 'The project no longer exists.', status: 409 };

  const attachmentId = randomUUID();
  const safeName = path.basename(file.name).replace(/[^A-Za-z0-9._ -]/g, '_');
  const relativePath = path.join(project.folder, '00 - Project Control', 'ENGCO ONE Uploads', taskId, `${attachmentId}-${safeName}`);
  const absolutePath = path.resolve(process.cwd(), '..', relativePath);
  const projectRoot = path.resolve(process.cwd(), '..', project.folder);
  if (!absolutePath.startsWith(`${projectRoot}${path.sep}`)) return { error: 'Invalid storage path.', status: 400 };

  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, bytes, { flag: 'wx' });
  const attachment: TaskAttachment = { id: attachmentId, name: safeName, size: file.size, mimeType: file.type, relativePath, uploadedAt: new Date().toISOString() };
  await addTaskAttachment(taskId, attachment);
  return attachment;
}
