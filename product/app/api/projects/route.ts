import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { NextResponse } from 'next/server';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');

export async function POST(request: Request) {
  const body = await request.json() as { name?: string; city?: string; client?: string; type?: string; phase?: string };
  const { name, city, client, type } = body;
  if (!name || !city || !client || !type) {
    return NextResponse.json({ error: 'Name, city, client, and type are required.' }, { status: 400 });
  }

  const args = [
    path.join(ROOT, 'scripts', 'new_project.py'),
    '--name', name, '--city', city, '--client', client, '--type', type,
  ];
  if (body.phase) args.push('--phase', body.phase);

  try {
    const { stdout } = await runFile('python3', args, { cwd: ROOT });
    return NextResponse.json({ ok: true, message: stdout.trim() }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error && 'stdout' in error
      ? String((error as { stdout?: string }).stdout || error.message)
      : 'Could not register the project.';
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
