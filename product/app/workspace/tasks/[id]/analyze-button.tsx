'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, ScanSearch } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function AnalyzeButton({ taskId, disabled }: { taskId: string; disabled: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function analyze() {
    setBusy(true);
    setError('');
    try {
      const response = await fetch(`/api/tasks/${taskId}/analyze`, { method: 'POST' });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Analysis failed.');
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Analysis failed.');
    } finally {
      setBusy(false);
    }
  }

  return <div className="space-y-2 text-right"><Button onClick={analyze} disabled={disabled || busy} className="bg-emerald-700 hover:bg-emerald-800">{busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <ScanSearch className="h-4 w-4" />} {busy ? 'Analyzing PDFs…' : 'Analyze PDFs'}</Button>{error && <p role="alert" className="text-sm text-destructive">{error}</p>}</div>;
}
