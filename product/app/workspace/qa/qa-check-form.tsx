'use client';

import { useRef, useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';

type PageCheck = { page: number; status: string; stamped_as?: string; expected?: string; note?: string };
type Result = {
  file: string;
  pdf_page_count: number;
  sheet_index_count: number;
  sheet_index: { sheet_no: string; title: string }[];
  issues: string[];
  page_checks: PageCheck[];
  error?: string;
};

export function QaCheckForm() {
  const input = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<Result | null>(null);

  async function run(file: File) {
    setBusy(true);
    setError('');
    setResult(null);
    const form = new FormData();
    form.set('file', file);
    try {
      const response = await fetch('/api/qa/check', { method: 'POST', body: form });
      const data = await response.json();
      if (!response.ok || data.error) throw new Error(data.error || 'Check failed.');
      setResult(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Check failed.');
    } finally {
      setBusy(false);
      if (input.current) input.current.value = '';
    }
  }

  return (
    <div className="space-y-5">
      <input ref={input} type="file" accept="application/pdf,.pdf" className="sr-only" onChange={(e) => { const f = e.target.files?.[0]; if (f) void run(f); }} />
      <Button type="button" disabled={busy} onClick={() => input.current?.click()} className="bg-emerald-700 hover:bg-emerald-800">
        {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />} {busy ? 'Checking…' : 'Upload a plan set PDF'}
      </Button>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

      {result && (
        <div className="space-y-4">
          <div className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${result.issues.length ? 'bg-red-50 text-red-800' : 'bg-emerald-50 text-emerald-800'}`}>
            {result.issues.length ? <AlertTriangle className="h-4 w-4 shrink-0" /> : <CheckCircle2 className="h-4 w-4 shrink-0" />}
            {result.issues.length
              ? `${result.issues.length} issue${result.issues.length === 1 ? '' : 's'} found`
              : `Clean — ${result.pdf_page_count} pages, all self-identified correctly`}
          </div>

          {!!result.issues.length && (
            <ul className="list-inside list-disc space-y-1 rounded-md border border-red-200 bg-red-50/50 p-3 text-sm text-red-900">
              {result.issues.map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          )}

          <div className="rounded-md border">
            <div className="grid grid-cols-4 gap-2 border-b bg-slate-50 p-2 text-xs font-medium uppercase text-muted-foreground">
              <span>Page</span><span>Status</span><span>Stamped as</span><span>Expected</span>
            </div>
            {result.page_checks.map((p) => (
              <div key={p.page} className={`grid grid-cols-4 gap-2 border-b p-2 text-sm last:border-0 ${p.status === 'MISMATCH' ? 'bg-red-50' : ''}`}>
                <span>{p.page}</span>
                <span className={p.status === 'match' ? 'text-emerald-700' : p.status === 'MISMATCH' ? 'font-medium text-red-700' : 'text-muted-foreground'}>{p.status}</span>
                <span>{p.stamped_as ?? '—'}</span>
                <span>{p.expected ?? '—'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
