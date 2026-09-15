'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Bot, Loader2, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

type Recommendation = {
  agent: { id: string; name: string; mission: string; accountable_owner: string; hard_boundaries: string; approval_gate: string };
  reason: string;
  confidence: string;
};

export function NewWorkForm({ projects }: { projects: { id: string; name: string }[] }) {
  const router = useRouter();
  const [projectId, setProjectId] = useState('');
  const [outcome, setOutcome] = useState('');
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function recommend() {
    setBusy(true);
    setError('');
    setRecommendation(null);
    try {
      const response = await fetch('/api/workflows/recommend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ outcome }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not recommend a workflow.');
      setRecommendation(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not recommend a workflow.');
    } finally {
      setBusy(false);
    }
  }

  async function create() {
    if (!recommendation) return;
    setBusy(true);
    setError('');
    try {
      const response = await fetch('/api/tasks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ outcome, projectId, agentId: recommendation.agent.id }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not create the task.');
      router.push(`/workspace/tasks/${result.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not create the task.');
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-[220px_1fr]">
        <select aria-label="Project" value={projectId} onChange={(event) => setProjectId(event.target.value)} className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring">
          <option value="" disabled>Select a project</option>
          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
        </select>
        <div className="relative">
          <Sparkles className="absolute left-3 top-3 h-4 w-4 text-emerald-600" />
          <textarea value={outcome} onChange={(event) => { setOutcome(event.target.value); setRecommendation(null); }} placeholder="What outcome do you need? Try: Review these drawings and prepare a benchmark estimate." className="min-h-28 w-full resize-none rounded-md border bg-background py-2.5 pl-10 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring" />
        </div>
      </div>

      {!recommendation && <div className="flex justify-end"><Button onClick={recommend} disabled={!projectId || !outcome.trim() || busy} className="bg-emerald-700 hover:bg-emerald-800">{busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />} Recommend a workflow</Button></div>}

      {recommendation && <section className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-5"><div className="flex items-start gap-3"><span className="rounded-md bg-emerald-700 p-2 text-white"><Bot className="h-5 w-5" /></span><div className="min-w-0 flex-1">
        <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Recommended agent · {recommendation.confidence} confidence</p>
        <h2 className="mt-1 text-lg font-semibold">{recommendation.agent.name}</h2>
        <p className="mt-1 text-sm text-muted-foreground">{recommendation.reason}</p>
        <p className="mt-4 text-sm">{recommendation.agent.mission}</p>
        <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2"><div className="rounded-md bg-white p-3"><strong className="mb-1 block">Human owner</strong>{recommendation.agent.accountable_owner}</div><div className="rounded-md bg-white p-3"><strong className="mb-1 flex items-center gap-1"><ShieldCheck className="h-4 w-4" /> Approval gate</strong>{recommendation.agent.approval_gate}</div></div>
        <details className="mt-3 text-sm"><summary className="cursor-pointer font-medium">Agent boundaries</summary><p className="mt-2 text-muted-foreground">{recommendation.agent.hard_boundaries}</p></details>
        <div className="mt-5 flex justify-end gap-2"><Button variant="outline" onClick={() => setRecommendation(null)} disabled={busy}>Change request</Button><Button onClick={create} disabled={busy} className="bg-emerald-700 hover:bg-emerald-800">{busy && <Loader2 className="h-4 w-4 animate-spin" />} Create task</Button></div>
      </div></div></section>}

      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
