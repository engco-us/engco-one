import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getTask } from '@/lib/engco/tasks';
import { AttachmentUpload } from './attachment-upload';
import { AnalyzeButton } from './analyze-button';

const STATUS_LABEL: Record<string, string> = {
  ready: 'Ready',
  processing: 'Analyzing…',
  needs_review: 'Needs review',
  failed: 'Failed',
};
const STATUS_COLOR: Record<string, string> = {
  ready: 'bg-emerald-100 text-emerald-800',
  processing: 'bg-amber-100 text-amber-800',
  needs_review: 'bg-blue-100 text-blue-800',
  failed: 'bg-red-100 text-red-800',
};

export default async function TaskPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const task = await getTask(id);
  if (!task) notFound();

  return (
    <div className="mx-auto max-w-3xl space-y-5 p-5 sm:p-10">
      <Button asChild variant="ghost" size="sm" className="-ml-3"><Link href="/workspace"><ArrowLeft className="h-4 w-4" /> New takeoff</Link></Button>

      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{task.title}</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{task.projectName}</p>
        </div>
        <span className={`w-fit rounded-full px-3 py-1 text-sm font-medium ${STATUS_COLOR[task.status] ?? 'bg-slate-100 text-slate-800'}`}>{STATUS_LABEL[task.status] ?? task.status}</span>
      </div>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">Results</CardTitle>
          <AnalyzeButton taskId={task.id} disabled={!task.attachments?.length} />
        </CardHeader>
        <CardContent>
          {task.analyses?.length ? (
            <div className="space-y-4">
              {task.analyses.map((analysis) => (
                <div key={analysis.attachmentId} className="rounded-md border p-4">
                  <p className="font-medium">{analysis.fileName}</p>
                  {analysis.error ? (
                    <p className="mt-1 text-sm text-destructive">{analysis.error}</p>
                  ) : (
                    <>
                      <p className="mt-1 text-sm text-muted-foreground">{analysis.pageCount} pages &middot; {analysis.unclassifiedCount} unclassified</p>
                      <div className="mt-3 space-y-1">
                        {analysis.pages.filter((p) => p.sheet_types.length).map((p) => (
                          <div key={p.page} className="flex items-center gap-2 text-sm">
                            <span className="w-14 shrink-0 font-mono text-muted-foreground">p.{p.page}</span>
                            <span className="flex flex-wrap gap-1">
                              {p.sheet_types.map((t) => <span key={t} className="rounded bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-800">{t}</span>)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No results yet.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">Source files</CardTitle>
          <AttachmentUpload taskId={task.id} />
        </CardHeader>
        <CardContent>
          {task.attachments?.length ? (
            <div className="divide-y rounded-md border">
              {task.attachments.map((attachment) => (
                <a key={attachment.id} href={`/api/tasks/${task.id}/attachments/${attachment.id}`} target="_blank" rel="noreferrer" className="flex items-center justify-between gap-4 p-3 hover:bg-slate-50">
                  <span className="flex min-w-0 items-center gap-3"><FileText className="h-5 w-5 shrink-0 text-emerald-700" /><span className="truncate font-medium">{attachment.name}</span></span>
                  <span className="shrink-0 text-sm text-muted-foreground">{formatBytes(attachment.size)}</span>
                </a>
              ))}
            </div>
          ) : <p className="text-sm text-muted-foreground">None.</p>}
        </CardContent>
      </Card>
    </div>
  );
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
