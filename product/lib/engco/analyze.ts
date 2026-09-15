import 'server-only';

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { getTask, setTaskAnalysis, type DocumentAnalysis, type QuantityMatch } from './tasks';

const runFile = promisify(execFile);

// Two separate, honest steps — never blur them into one "result":
// classify_sheets.py tags what's on each page (works on anything, finds
// no numbers). auto_extract.py runs only the extractors this toolkit has
// real proof on and says plainly when none matched, rather than letting a
// page-tag list stand in for a quantity takeoff it never produced.
export async function analyzeTaskDocuments(taskId: string) {
  const task = await getTask(taskId);
  if (!task) throw new Error('Task not found.');
  if (!task.attachments?.length) throw new Error('Upload at least one PDF before analysis.');

  await setTaskAnalysis(taskId, 'processing', task.analyses ?? []);
  const repoRoot = path.resolve(process.cwd(), '..');
  const classifyScript = path.join(repoRoot, 'scripts', 'estimating', 'classify_sheets.py');
  const autoExtractScript = path.join(repoRoot, 'scripts', 'estimating', 'auto_extract.py');
  const analyses: DocumentAnalysis[] = [];

  for (const attachment of task.attachments) {
    const absolutePdf = path.resolve(repoRoot, attachment.relativePath);
    if (!absolutePdf.startsWith(`${repoRoot}${path.sep}`)) throw new Error('Invalid attachment path.');
    try {
      const [classifyRun, autoExtractRun] = await Promise.all([
        runFile('python3', [classifyScript, absolutePdf], { cwd: repoRoot, maxBuffer: 20 * 1024 * 1024, timeout: 5 * 60 * 1000 }),
        runFile('python3', [autoExtractScript, absolutePdf], { cwd: repoRoot, maxBuffer: 20 * 1024 * 1024, timeout: 5 * 60 * 1000 }),
      ]);
      const manifest = JSON.parse(classifyRun.stdout) as { page_count: number; unclassified_count: number; pages: DocumentAnalysis['pages'] };
      const autoExtract = JSON.parse(autoExtractRun.stdout) as { matched_count: number; matched: QuantityMatch[]; note: string | null };
      analyses.push({
        attachmentId: attachment.id,
        fileName: attachment.name,
        pageCount: manifest.page_count,
        unclassifiedCount: manifest.unclassified_count,
        pages: manifest.pages,
        quantities: autoExtract.matched,
        quantitiesNote: autoExtract.note,
        analyzedAt: new Date().toISOString(),
      });
    } catch (error) {
      analyses.push({
        attachmentId: attachment.id, fileName: attachment.name, pageCount: 0, unclassifiedCount: 0,
        pages: [], quantities: [], quantitiesNote: null,
        analyzedAt: new Date().toISOString(), error: error instanceof Error ? error.message : 'Analysis failed.',
      });
    }
  }

  const failed = analyses.every((analysis) => analysis.error);
  return setTaskAnalysis(taskId, failed ? 'failed' : 'needs_review', analyses);
}
