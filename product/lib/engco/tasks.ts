import 'server-only';

import { randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';

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

export type DocumentAnalysis = {
  attachmentId: string;
  fileName: string;
  pageCount: number;
  unclassifiedCount: number;
  pages: { page: number; sheet_types: string[]; note?: string }[];
  analyzedAt: string;
  error?: string;
};

const dataRoot = path.resolve(process.cwd(), '..', 'data');
const tasksPath = path.join(dataRoot, 'tasks.json');

async function readTasks(): Promise<Task[]> {
  try {
    const value = JSON.parse(await readFile(tasksPath, 'utf8')) as { tasks?: Task[] };
    return value.tasks ?? [];
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return [];
    throw error;
  }
}

export async function createTask(input: Omit<Task, 'id' | 'title' | 'status' | 'createdAt' | 'attachments' | 'analyses'>) {
  const task: Task = {
    ...input,
    id: randomUUID(),
    title: input.outcome.trim().replace(/\s+/g, ' ').slice(0, 80),
    status: 'ready',
    createdAt: new Date().toISOString(),
    attachments: [],
    analyses: []
  };
  const tasks = await readTasks();
  tasks.unshift(task);
  await mkdir(dataRoot, { recursive: true });
  const temporaryPath = `${tasksPath}.${process.pid}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify({ tasks }, null, 2)}\n`, 'utf8');
  await rename(temporaryPath, tasksPath);
  return task;
}

export async function getTask(id: string) {
  return (await readTasks()).find((task) => task.id === id) ?? null;
}

export async function addTaskAttachment(taskId: string, attachment: TaskAttachment) {
  const tasks = await readTasks();
  const task = tasks.find((candidate) => candidate.id === taskId);
  if (!task) return null;
  task.attachments = [...(task.attachments ?? []), attachment];
  const temporaryPath = `${tasksPath}.${process.pid}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify({ tasks }, null, 2)}\n`, 'utf8');
  await rename(temporaryPath, tasksPath);
  return task;
}

export async function setTaskAnalysis(taskId: string, status: Task['status'], analyses: DocumentAnalysis[]) {
  const tasks = await readTasks();
  const task = tasks.find((candidate) => candidate.id === taskId);
  if (!task) return null;
  task.status = status;
  task.analyses = analyses;
  const temporaryPath = `${tasksPath}.${process.pid}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify({ tasks }, null, 2)}\n`, 'utf8');
  await rename(temporaryPath, tasksPath);
  return task;
}
