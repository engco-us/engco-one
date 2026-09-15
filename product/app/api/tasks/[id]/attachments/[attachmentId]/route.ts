import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { NextResponse } from 'next/server';
import { getTask } from '@/lib/engco/tasks';

export const runtime = 'nodejs';

export async function GET(_request: Request, { params }: { params: Promise<{ id: string; attachmentId: string }> }) {
  const { id, attachmentId } = await params;
  const task = await getTask(id);
  const attachment = task?.attachments?.find((candidate) => candidate.id === attachmentId);
  if (!attachment) return NextResponse.json({ error: 'Attachment not found.' }, { status: 404 });

  const dataRoot = path.resolve(process.cwd(), '..');
  const absolutePath = path.resolve(dataRoot, attachment.relativePath);
  if (!absolutePath.startsWith(`${dataRoot}${path.sep}`)) return NextResponse.json({ error: 'Invalid attachment path.' }, { status: 400 });
  const bytes = await readFile(absolutePath);
  return new Response(bytes, { headers: { 'Content-Type': attachment.mimeType, 'Content-Length': String(bytes.length), 'Content-Disposition': `inline; filename*=UTF-8''${encodeURIComponent(attachment.name)}` } });
}
