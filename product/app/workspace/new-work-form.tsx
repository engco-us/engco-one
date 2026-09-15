'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, UploadCloud } from 'lucide-react';

export function NewWorkForm({ projects }: { projects: { id: string; name: string }[] }) {
  const router = useRouter();
  const input = useRef<HTMLInputElement>(null);
  const [projectId, setProjectId] = useState('');
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');

  async function run(file: File) {
    if (!projectId) { setError('Pick a project first.'); return; }
    setBusy(true);
    setError('');
    const form = new FormData();
    form.set('projectId', projectId);
    form.set('file', file);
    try {
      const response = await fetch('/api/quick-takeoff', { method: 'POST', body: form });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not run the takeoff.');
      router.push(`/workspace/tasks/${result.taskId}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not run the takeoff.');
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <select
        aria-label="Project"
        value={projectId}
        onChange={(e) => setProjectId(e.target.value)}
        className="h-11 w-full rounded-md border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
      >
        <option value="">Pick a project</option>
        {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>

      <input
        ref={input}
        type="file"
        accept="application/pdf,.pdf"
        className="sr-only"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) void run(f); }}
      />
      <button
        type="button"
        disabled={busy || !projectId}
        onClick={() => input.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files?.[0]; if (f) void run(f); }}
        className={`flex w-full flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed py-16 text-center transition-colors ${
          dragOver ? 'border-emerald-500 bg-emerald-50' : 'border-slate-300 hover:border-emerald-400 hover:bg-slate-50'
        } ${!projectId ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
      >
        {busy ? (
          <>
            <Loader2 className="h-8 w-8 animate-spin text-emerald-700" />
            <p className="text-sm font-medium text-emerald-700">Running the takeoff&hellip;</p>
          </>
        ) : (
          <>
            <UploadCloud className="h-8 w-8 text-slate-400" />
            <p className="text-sm font-medium">Drop a plan set PDF, or click to browse</p>
          </>
        )}
      </button>

      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
