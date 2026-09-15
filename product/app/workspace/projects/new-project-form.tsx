'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const PHASES = ['Discovery', 'Feasibility', 'Design', 'Permitting', 'Preconstruction', 'Construction', 'Closeout'];

export function NewProjectForm() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [city, setCity] = useState('');
  const [client, setClient] = useState('');
  const [type, setType] = useState('');
  const [phase, setPhase] = useState('Discovery');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, city, client, type, phase }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not register the project.');
      setName(''); setCity(''); setClient(''); setType(''); setPhase('Discovery');
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not register the project.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
      <div><Label htmlFor="name">Project name</Label><Input id="name" required value={name} onChange={(e) => setName(e.target.value)} /></div>
      <div><Label htmlFor="city">City</Label><Input id="city" required value={city} onChange={(e) => setCity(e.target.value)} /></div>
      <div><Label htmlFor="client">Client</Label><Input id="client" required value={client} onChange={(e) => setClient(e.target.value)} /></div>
      <div><Label htmlFor="type">Project type</Label><Input id="type" required value={type} onChange={(e) => setType(e.target.value)} /></div>
      <div>
        <Label htmlFor="phase">Starting phase</Label>
        <select id="phase" value={phase} onChange={(e) => setPhase(e.target.value)} className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm">
          {PHASES.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>
      <div className="flex items-end sm:col-span-2">
        <Button type="submit" disabled={busy} className="bg-emerald-700 hover:bg-emerald-800">
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />} Register project
        </Button>
      </div>
      {error && <p role="alert" className="text-sm text-destructive sm:col-span-2">{error}</p>}
    </form>
  );
}
