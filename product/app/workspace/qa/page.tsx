import { Card, CardContent } from '@/components/ui/card';
import { QaCheckForm } from './qa-check-form';

export default function QaPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">DESIGN QA</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Sheet index check</h1>
        <p className="mt-3 text-muted-foreground">Catches a real, common mistake before a human finds it by flipping through every page: a missing sheet, an extra sheet, or two sheets swapped out of order. Cross-checks the cover sheet&apos;s printed index against every page&apos;s own self-identifying stamp — nothing guessed.</p>
      </section>
      <Card className="border-slate-200 shadow-sm"><CardContent className="pt-6"><QaCheckForm /></CardContent></Card>
    </div>
  );
}
