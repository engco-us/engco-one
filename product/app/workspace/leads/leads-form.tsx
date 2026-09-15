'use client';

import { useState } from 'react';
import { Loader2, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const SOURCES = [
  { id: 'esbd', label: 'TxDOT (ESBD) — no key needed', defaultOn: true },
  { id: 'austin', label: 'Austin commercial building permits', defaultOn: true },
  { id: 'samgov', label: 'SAM.gov (federal) — needs SAM_GOV_API_KEY set', defaultOn: false },
];

export function LeadsForm() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [output, setOutput] = useState('');
  const [daysBack, setDaysBack] = useState(14);
  const [selected, setSelected] = useState<string[]>(SOURCES.filter((s) => s.defaultOn).map((s) => s.id));

  function toggle(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  }

  async function run(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    setOutput('');
    try {
      const response = await fetch('/api/leads/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sources: selected, daysBack }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Run failed.');
      setOutput(result.output);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Run failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <form onSubmit={run} className="space-y-4">
        <div className="max-w-[200px]"><Label htmlFor="days">Look back this many days</Label><Input id="days" type="number" value={daysBack} onChange={(e) => setDaysBack(Number(e.target.value))} /></div>
        <div className="space-y-2">
          {SOURCES.map((s) => (
            <label key={s.id} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={selected.includes(s.id)} onChange={() => toggle(s.id)} className="h-4 w-4" />
              {s.label}
            </label>
          ))}
        </div>
        <Button type="submit" disabled={busy} className="bg-emerald-700 hover:bg-emerald-800">
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} {busy ? 'Running…' : 'Run'}
        </Button>
        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      </form>
      {output && <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs text-slate-100">{output}</pre>}
    </div>
  );
}
