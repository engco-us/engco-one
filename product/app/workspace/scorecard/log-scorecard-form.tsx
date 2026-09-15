'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function LogScorecardForm({ derived }: { derived: { active_projects: number; proposals_out: number; proposals_out_detail: string[] } }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);
  const [cashPosition, setCashPosition] = useState('');
  const [recordedBy, setRecordedBy] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    setDone(false);
    try {
      const response = await fetch('/api/scorecard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cashPosition: Number(cashPosition), recordedBy }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not log the entry.');
      setDone(true);
      setCashPosition('');
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not log the entry.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border bg-slate-50 p-3"><p className="text-2xl font-semibold">{derived.active_projects}</p><p className="text-xs text-muted-foreground">active projects (derived)</p></div>
        <div className="rounded-md border bg-slate-50 p-3">
          <p className="text-2xl font-semibold">{derived.proposals_out}</p>
          <p className="text-xs text-muted-foreground">proposals out (derived)</p>
          {!!derived.proposals_out_detail.length && <p className="mt-1 text-xs text-muted-foreground">{derived.proposals_out_detail.join(', ')}</p>}
        </div>
      </div>

      <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
        <div><Label htmlFor="cash">Cash position ($)</Label><Input id="cash" type="number" required value={cashPosition} onChange={(e) => setCashPosition(e.target.value)} /></div>
        <div><Label htmlFor="by">Recorded by</Label><Input id="by" required value={recordedBy} onChange={(e) => setRecordedBy(e.target.value)} /></div>
        <div className="flex items-end gap-3 sm:col-span-2">
          <Button type="submit" disabled={busy} className="bg-emerald-700 hover:bg-emerald-800">{busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null} Log this week</Button>
          {done && <span className="flex items-center gap-1 text-sm text-emerald-700"><CheckCircle2 className="h-4 w-4" /> Logged</span>}
        </div>
        {error && <p role="alert" className="text-sm text-destructive sm:col-span-2">{error}</p>}
      </form>
    </div>
  );
}
