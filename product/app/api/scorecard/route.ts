import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { NextResponse } from 'next/server';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');

export async function POST(request: Request) {
  const body = await request.json() as { cashPosition?: number; recordedBy?: string; weekOf?: string; notes?: string };
  if (body.cashPosition === undefined || body.cashPosition === null || !body.recordedBy) {
    return NextResponse.json({ error: 'Cash position and recorded-by are required.' }, { status: 400 });
  }

  const args = [
    path.join(ROOT, 'scripts', 'scorecard_auto.py'), '--add',
    '--cash-position', String(body.cashPosition),
    '--recorded-by', body.recordedBy,
  ];
  if (body.weekOf) args.push('--week-of', body.weekOf);
  if (body.notes) args.push('--notes', body.notes);

  try {
    const { stdout } = await runFile('python3', args, { cwd: ROOT });
    return NextResponse.json({ ok: true, message: stdout.trim() }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error && 'stdout' in error
      ? String((error as { stdout?: string }).stdout || error.message)
      : 'Could not log the scorecard entry.';
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
