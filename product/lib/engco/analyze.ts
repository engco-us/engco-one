import 'server-only';

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { getTask, setTaskAnalysis, type DocumentAnalysis } from './tasks';

const runFile = promisify(execFile);

export async function analyzeTaskDocuments(taskId: string) {
  const task = await getTask(taskId);
  if (!task) throw new Error('Task not found.');
  if (!task.attachments?.length) throw new Error('Upload at least one PDF before analysis.');

  await setTaskAnalysis(taskId, 'processing', task.analyses ?? []);
  const repoRoot = path.resolve(process.cwd(), '..');
  const script = path.join(repoRoot, 'scripts', 'estimating', 'classify_sheets.py');
  const analyses: DocumentAnalysis[] = [];

  for (const attachment of task.attachments) {
    const absolutePdf = path.resolve(repoRoot, attachment.relativePath);
    if (!absolutePdf.startsWith(`${repoRoot}${path.sep}`)) throw new Error('Invalid attachment path.');
    try {
      const { stdout } = await runFile('python3', [script, absolutePdf], { cwd: repoRoot, maxBuffer: 20 * 1024 * 1024, timeout: 5 * 60 * 1000 });
      const manifest = JSON.parse(stdout) as { page_count: number; unclassified_count: number; pages: DocumentAnalysis['pages'] };
      analyses.push({ attachmentId: attachment.id, fileName: attachment.name, pageCount: manifest.page_count, unclassifiedCount: manifest.unclassified_count, pages: manifest.pages, analyzedAt: new Date().toISOString() });
    } catch (error) {
      analyses.push({ attachmentId: attachment.id, fileName: attachment.name, pageCount: 0, unclassifiedCount: 0, pages: [], analyzedAt: new Date().toISOString(), error: error instanceof Error ? error.message : 'Analysis failed.' });
    }
  }

  const failed = analyses.every((analysis) => analysis.error);
  return setTaskAnalysis(taskId, failed ? 'failed' : 'needs_review', analyses);
}
