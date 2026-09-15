import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { NextResponse } from 'next/server';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');
const maxBytes = 80 * 1024 * 1024;

export async function POST(request: Request) {
  const form = await request.formData();
  const file = form.get('file');
  if (!(file instanceof File)) return NextResponse.json({ error: 'Choose a PDF file.' }, { status: 400 });
  if (file.size === 0 || file.size > maxBytes) return NextResponse.json({ error: 'PDF must be between 1 byte and 80 MB.' }, { status: 400 });

  const bytes = Buffer.from(await file.arrayBuffer());
  if (file.type !== 'application/pdf' || bytes.subarray(0, 5).toString() !== '%PDF-') {
    return NextResponse.json({ error: 'Only a valid PDF is accepted.' }, { status: 415 });
  }

  const dir = await mkdtemp(path.join(tmpdir(), 'engco-qa-'));
  const pdfPath = path.join(dir, path.basename(file.name).replace(/[^A-Za-z0-9._ -]/g, '_'));
  try {
    await writeFile(pdfPath, bytes);
    const { stdout } = await runFile('python3', [path.join(ROOT, 'scripts', 'qa', 'check_sheet_index.py'), pdfPath], { cwd: ROOT, maxBuffer: 20 * 1024 * 1024 });
    // The script prints the JSON result, then a blank line, then a
    // human-readable summary for terminal use — only the first part is JSON.
    const jsonPart = stdout.split('\n\n')[0];
    return NextResponse.json(JSON.parse(jsonPart));
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Check failed.';
    return NextResponse.json({ error: message }, { status: 500 });
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}
