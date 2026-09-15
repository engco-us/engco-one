import { NextResponse } from 'next/server';
import { analyzeTaskDocuments } from '@/lib/engco/analyze';

export const runtime = 'nodejs';
export const maxDuration = 300;

export async function POST(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const task = await analyzeTaskDocuments(id);
    return NextResponse.json(task);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Analysis failed.';
    return NextResponse.json({ error: message }, { status: message === 'Task not found.' ? 404 : 400 });
  }
}
