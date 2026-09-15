import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { NextResponse } from 'next/server';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');

export async function GET() {
  const { stdout } = await runFile('python3', [path.join(ROOT, 'scripts', 'scorecard_auto.py')], { cwd: ROOT });
  return NextResponse.json(JSON.parse(stdout));
}
