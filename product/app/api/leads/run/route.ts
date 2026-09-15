import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { NextResponse } from 'next/server';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');

export async function POST(request: Request) {
  const body = await request.json() as { sources?: string[]; daysBack?: number };
  const sources = body.sources ?? [];
  const daysBack = String(body.daysBack ?? 14);
  const output: string[] = [];

  if (sources.includes('esbd')) {
    const r = await runFile('python3', [path.join(ROOT, 'scripts', 'leads', 'fetch_esbd.py'), '--days-back', daysBack], { cwd: ROOT }).catch((e) => e);
    output.push(`=== ESBD / TxDOT ===\n${(r.stderr || r.stdout || '').toString().trim()}`);
  }
  if (sources.includes('austin')) {
    const r = await runFile('python3', [path.join(ROOT, 'scripts', 'leads', 'fetch_austin_permits.py'), '--days-back', daysBack], { cwd: ROOT }).catch((e) => e);
    const text = (r.stdout || r.stderr || '').toString().trim();
    const tail = text.split('\n').filter(Boolean).at(-1) ?? text;
    output.push(`=== Austin Permits ===\n${tail}`);
  }
  if (sources.includes('samgov')) {
    const r = await runFile('python3', [path.join(ROOT, 'scripts', 'leads', 'fetch_samgov.py'), '--days-back', daysBack], { cwd: ROOT }).catch((e) => e);
    output.push(`=== SAM.gov ===\n${(r.stdout || r.stderr || '').toString().trim()}`);
  }

  return NextResponse.json({ output: output.join('\n\n') || 'No sources selected.' });
}
