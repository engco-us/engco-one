import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { readFile } from 'node:fs/promises';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LogScorecardForm } from './log-scorecard-form';

const runFile = promisify(execFile);
const ROOT = path.resolve(process.cwd(), '..');

type Entry = { week_of: string; active_projects: number; proposals_out: number; cash_position: number; recorded_by: string; notes: string };

export default async function ScorecardPage() {
  const [{ stdout }, raw] = await Promise.all([
    runFile('python3', [path.join(ROOT, 'scripts', 'scorecard_auto.py')], { cwd: ROOT }),
    readFile(path.join(ROOT, 'data', 'scorecard.json'), 'utf8'),
  ]);
  const derived = JSON.parse(stdout) as { active_projects: number; proposals_out: number; proposals_out_detail: string[] };
  const entries = (JSON.parse(raw).entries as Entry[]).slice().reverse();

  return (
    <div className="mx-auto max-w-4xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">SCORECARD</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Weekly scorecard</h1>
        <p className="mt-3 text-muted-foreground">Active projects and proposals out are derived live from the real project registry — only cash position needs a human, since there&apos;s no accounting system connected yet.</p>
      </section>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader><CardTitle>Log this week</CardTitle></CardHeader>
        <CardContent><LogScorecardForm derived={derived} /></CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>History</CardTitle></CardHeader>
        <CardContent>
          <div className="divide-y rounded-md border">
            {entries.map((e) => (
              <div key={e.week_of} className="grid gap-1 p-3 text-sm sm:grid-cols-5 sm:items-center">
                <span className="font-medium">{e.week_of}</span>
                <span>{e.active_projects} active</span>
                <span>{e.proposals_out} proposal{e.proposals_out === 1 ? '' : 's'} out</span>
                <span>${e.cash_position.toLocaleString()}</span>
                <span className="text-xs text-muted-foreground">by {e.recorded_by}</span>
              </div>
            ))}
            {!entries.length && <p className="p-3 text-sm text-muted-foreground">No entries yet.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
