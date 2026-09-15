import Link from 'next/link';
import { notFound } from 'next/navigation';
import { AlertTriangle, ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getTask, type QuantityMatch } from '@/lib/engco/tasks';
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
          <CardTitle className="text-base">Quantities</CardTitle>
          <AnalyzeButton taskId={task.id} disabled={!task.attachments?.length} />
        </CardHeader>
        <CardContent>
          {!task.analyses?.length && <p className="text-sm text-muted-foreground">No results yet.</p>}
          {task.analyses?.map((analysis) => (
            <div key={analysis.attachmentId} className="space-y-3">
              {analysis.error && <p className="text-sm text-destructive">{analysis.error}</p>}
              {!analysis.error && analysis.quantities.length > 0 && analysis.quantities.map((q, i) => <QuantityCard key={i} match={q} />)}
              {!analysis.error && analysis.quantities.length === 0 && analysis.quantitiesNote && (
                <div className="flex gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                  <AlertTriangle className="h-4 w-4 shrink-0 translate-y-0.5" />
                  <p>{analysis.quantitiesNote}</p>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {!!task.analyses?.length && (
        <details className="rounded-lg border bg-white">
          <summary className="cursor-pointer select-none px-5 py-3 text-sm font-medium">What&apos;s on each page ({task.analyses[0]?.pageCount ?? 0} pages)</summary>
          <div className="space-y-1 px-5 pb-4">
            {task.analyses[0]?.pages.filter((p) => p.sheet_types.length).map((p) => (
              <div key={p.page} className="flex items-center gap-2 text-sm">
                <span className="w-14 shrink-0 font-mono text-muted-foreground">p.{p.page}</span>
                <span className="flex flex-wrap gap-1">
                  {p.sheet_types.map((t) => <span key={t} className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">{t}</span>)}
                </span>
              </div>
            ))}
          </div>
        </details>
      )}

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

function QuantityCard({ match }: { match: QuantityMatch }) {
  if (match.extractor === 'comcheck' || match.extractor === 'rescheck') {
    const r = match.result ?? {};
    const area = match.extractor === 'comcheck' ? r.floor_area_sf : r.conditioned_floor_area_sf;
    return (
      <div className="rounded-md border p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">{match.extractor === 'comcheck' ? 'COMcheck' : 'REScheck'}</p>
        <p className="mt-1 text-2xl font-semibold">{typeof area === 'number' ? area.toLocaleString() : '—'} <span className="text-sm font-normal text-muted-foreground">SF floor area</span></p>
      </div>
    );
  }
  if (match.extractor === 'txdot_eq') {
    const rows = match.rows ?? [];
    return (
      <div className="rounded-md border p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">TxDOT Estimate &amp; Quantity</p>
        <p className="mt-1 text-sm text-muted-foreground">{rows.length} bid item{rows.length === 1 ? '' : 's'}</p>
        <div className="mt-2 divide-y">
          {rows.map((row, i) => (
            <div key={i} className="flex items-center justify-between py-1.5 text-sm">
              <span className="min-w-0 truncate">{String(row.description)}</span>
              <span className="shrink-0 font-mono text-muted-foreground">{String(row.est_quantity)} {String(row.unit)}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  if (match.extractor === 'door_schedule') {
    const pages = match.pages ?? [];
    const totalDoors = pages.reduce((sum, p) => sum + (Number(p.door_count) || 0), 0);
    const totalArea = pages.reduce((sum, p) => sum + (Number(p.total_door_area_sf) || 0), 0);
    return (
      <div className="rounded-md border p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Door schedule</p>
        <p className="mt-1 text-2xl font-semibold">{totalDoors} <span className="text-sm font-normal text-muted-foreground">doors &middot; {totalArea.toLocaleString()} SF leaf area</span></p>
      </div>
    );
  }
  return null;
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
