import { getAgentRegistry } from '@/lib/engco/data';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const REAL_TOOLING: Record<string, string> = {
  'A-05': 'Real: classify_sheets.py + extractors, wired into New Work → Analyze PDFs.',
  'A-04': 'Real: check_sheet_index.py (scripts/qa) — catches a missing/swapped plan sheet.',
  'A-06': 'Real: scorecard_auto.py derives active projects + proposals out from the registry.',
  'A-02': 'Real leads-finder connectors exist (ESBD, Austin permits, SAM.gov) — see Leads Finder.',
};

export default async function AgentsPage() {
  const { agents, unowned_functions } = await getAgentRegistry();

  return (
    <div className="mx-auto max-w-5xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">AGENTS</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Agent registry</h1>
        <p className="mt-3 text-muted-foreground">These are governed roles, not autonomous processes — each has a real human owner and approval gate. Only some have real tooling behind them yet; that&apos;s called out on each card, not hidden.</p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2">
        {agents.map((agent) => (
          <Card key={agent.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{agent.name}</CardTitle>
                <span className="font-mono text-xs text-muted-foreground">{agent.id}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>{agent.mission}</p>
              <p className="text-xs text-muted-foreground"><span className="font-medium text-foreground">Owner:</span> {agent.accountable_owner}</p>
              <p className="text-xs text-muted-foreground"><span className="font-medium text-foreground">Approval gate:</span> {agent.approval_gate}</p>
              <p className="text-xs text-muted-foreground"><span className="font-medium text-foreground">Boundaries:</span> {agent.hard_boundaries}</p>
              <div className={`mt-2 rounded-md px-3 py-2 text-xs ${REAL_TOOLING[agent.id] ? 'bg-emerald-50 text-emerald-800' : 'bg-slate-100 text-slate-600'}`}>
                {REAL_TOOLING[agent.id] ?? 'No real tooling yet — role definition only.'}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!!unowned_functions?.length && (
        <Card>
          <CardHeader><CardTitle>Not yet owned by any agent</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {unowned_functions.map((f) => (
                <li key={f.function}>
                  <span className="font-medium">{f.function}</span>
                  <span className="ml-2 text-xs text-muted-foreground">{f.note}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
