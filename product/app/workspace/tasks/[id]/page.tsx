import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Bot, Calendar, FileText, FolderKanban } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getTask } from '@/lib/engco/tasks';
import { AttachmentUpload } from './attachment-upload';

export default async function TaskPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const task = await getTask(id);
  if (!task) notFound();

  return <main className="min-h-screen bg-slate-50 p-5 sm:p-10"><div className="mx-auto max-w-4xl space-y-6">
    <Button asChild variant="ghost" className="-ml-3"><Link href="/workspace"><ArrowLeft className="h-4 w-4" /> New work</Link></Button>
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-sm font-medium text-emerald-700">TASK</p><h1 className="mt-1 text-3xl font-semibold tracking-tight">{task.title}</h1></div><span className="w-fit rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-800">Ready</span></div>
    <Card><CardHeader><CardTitle>Requested outcome</CardTitle></CardHeader><CardContent><p className="leading-7">{task.outcome}</p></CardContent></Card>
    <Card><CardHeader className="flex-row items-center justify-between"><div><CardTitle>Source files</CardTitle><p className="mt-1 text-sm text-muted-foreground">PDFs are stored locally inside this project.</p></div><AttachmentUpload taskId={task.id} /></CardHeader><CardContent>
      {task.attachments?.length ? <div className="divide-y rounded-md border">{task.attachments.map((attachment) => <a key={attachment.id} href={`/api/tasks/${task.id}/attachments/${attachment.id}`} target="_blank" rel="noreferrer" className="flex items-center justify-between gap-4 p-3 hover:bg-slate-50"><span className="flex min-w-0 items-center gap-3"><FileText className="h-5 w-5 shrink-0 text-emerald-700" /><span className="truncate font-medium">{attachment.name}</span></span><span className="shrink-0 text-sm text-muted-foreground">{formatBytes(attachment.size)}</span></a>)}</div> : <p className="text-sm text-muted-foreground">No source files attached.</p>}
    </CardContent></Card>
    <div className="grid gap-4 sm:grid-cols-3"><Fact icon={FolderKanban} label="Project" value={task.projectName} /><Fact icon={Bot} label="Assigned agent" value={task.agentName} /><Fact icon={Calendar} label="Created" value={new Date(task.createdAt).toLocaleString()} /></div>
  </div></main>;
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function Fact({ icon: Icon, label, value }: { icon: typeof Bot; label: string; value: string }) {
  return <Card><CardContent className="pt-6"><Icon className="mb-4 h-5 w-5 text-emerald-700" /><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></CardContent></Card>;
}
