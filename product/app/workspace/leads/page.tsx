import { Card, CardContent } from '@/components/ui/card';
import { LeadsForm } from './leads-form';

export default function LeadsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">LEADS FINDER</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Find real work</h1>
        <p className="mt-3 text-muted-foreground">Report-only. Runs the real ESBD/Austin/SAM.gov connectors and reports what they find — never submits a bid, never contacts an agency.</p>
      </section>
      <Card className="border-slate-200 shadow-sm"><CardContent className="pt-6"><LeadsForm /></CardContent></Card>
    </div>
  );
}
