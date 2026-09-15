import { NextResponse } from 'next/server';
import { recommendWorkflow } from '@/lib/engco/workflows';

export async function POST(request: Request) {
  const body = await request.json() as { outcome?: string };
  const outcome = body.outcome?.trim();
  if (!outcome) return NextResponse.json({ error: 'Describe the outcome first.' }, { status: 400 });
  return NextResponse.json(await recommendWorkflow(outcome));
}
