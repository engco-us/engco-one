import 'server-only';

import { eq, sql } from 'drizzle-orm';
import { db } from '@/lib/db/drizzle';
import { tasks as tasksTable, type TaskRow } from '@/lib/db/schema';

export type Task = {
  id: string;
  title: string;
  outcome: string;
  projectId: string;
  projectName: string;
  agentId: string;
  agentName: string;
  status: 'ready' | 'processing' | 'needs_review' | 'failed';
  createdAt: string;
  attachments: TaskAttachment[];
  analyses: DocumentAnalysis[];
};

export type TaskAttachment = {
  id: string;
  name: string;
  size: number;
  mimeType: string;
  relativePath: string;
  uploadedAt: string;
};

export type QuantityMatch = {
  extractor: 'comcheck' | 'rescheck' | 'txdot_eq' | 'door_schedule' | 'hcfcd_detention';
  result?: Record<string, unknown>;
  rows?: Record<string, unknown>[];
  pages?: Record<string, unknown>[];
};

export type DocumentAnalysis = {
  attachmentId: string;
  fileName: string;
  pageCount: number;
  unclassifiedCount: number;
  pages: { page: number; sheet_types: string[]; note?: string }[];
  quantities: QuantityMatch[];
  quantitiesNote: string | null;
  analyzedAt: string;
  error?: string;
};

function serialize(row: TaskRow): Task {
  return {
    id: row.id,
    title: row.title,
    outcome: row.outcome,
    projectId: row.projectId,
    projectName: row.projectName,
    agentId: row.agentId,
    agentName: row.agentName,
    status: row.status as Task['status'],
    createdAt: row.createdAt.toISOString(),
    attachments: row.attachments as TaskAttachment[],
    analyses: row.analyses as DocumentAnalysis[]
  };
}

export async function createTask(
  input: Omit<Task, 'id' | 'title' | 'status' | 'createdAt' | 'attachments' | 'analyses'>
) {
  const [row] = await db
    .insert(tasksTable)
    .values({
      title: input.outcome.trim().replace(/\s+/g, ' ').slice(0, 80),
      outcome: input.outcome,
      projectId: input.projectId,
      projectName: input.projectName,
      agentId: input.agentId,
      agentName: input.agentName
    })
    .returning();
  return serialize(row);
}

export async function getTask(id: string) {
  const [row] = await db.select().from(tasksTable).where(eq(tasksTable.id, id)).limit(1);
  return row ? serialize(row) : null;
}

export async function addTaskAttachment(taskId: string, attachment: TaskAttachment) {
  // Appends via a single atomic UPDATE (jsonb || jsonb) instead of read-then-write,
  // so two uploads landing at the same time can't clobber each other.
  const [row] = await db
    .update(tasksTable)
    .set({ attachments: sql`${tasksTable.attachments} || ${JSON.stringify([attachment])}::jsonb` })
    .where(eq(tasksTable.id, taskId))
    .returning();
  return row ? serialize(row) : null;
}

export async function setTaskAnalysis(taskId: string, status: Task['status'], analyses: DocumentAnalysis[]) {
  const [row] = await db
    .update(tasksTable)
    .set({ status, analyses: analyses as unknown as object })
    .where(eq(tasksTable.id, taskId))
    .returning();
  return row ? serialize(row) : null;
}
