import Link from 'next/link';
import { Bot, ClipboardCheck, FileOutput, FolderKanban, Home, Library, ListTodo, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { getWorkspaceSnapshot } from '@/lib/engco/data';
import { NewWorkForm } from './new-work-form';

const nav = [[Home, 'Home'], [ListTodo, 'Work'], [FolderKanban, 'Projects'], [Bot, 'Agents'], [ClipboardCheck, 'Approvals'], [FileOutput, 'Deliverables'], [Library, 'Knowledge'], [Settings, 'Settings']] as const;

export default async function WorkspacePage() {
  const data = await getWorkspaceSnapshot();

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <div className="mx-auto grid min-h-screen max-w-[1600px] md:grid-cols-[240px_1fr]">
        <aside className="hidden border-r bg-slate-950 p-5 text-slate-100 md:flex md:flex-col">
          <Link href="/workspace" className="mb-8 flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-lg bg-emerald-500 font-bold text-slate-950">E1</span>
            <span><strong className="block">ENGCO ONE</strong><small className="text-slate-400">Operations workspace</small></span>
          </Link>
          <nav className="space-y-1">
            {nav.map(([Icon, label], index) => <Button key={label} variant="ghost" className={`w-full justify-start text-slate-300 hover:bg-slate-800 hover:text-white ${index === 0 ? 'bg-slate-800 text-white' : ''}`}><Icon className="h-4 w-4" /> {label}</Button>)}
          </nav>
        </aside>

        <section className="min-w-0">
          <div className="mx-auto max-w-5xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
            <section><p className="mb-2 text-sm font-medium text-emerald-700">NEW WORK</p><h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">What needs to get done?</h1><p className="mt-3 text-muted-foreground">Choose a project and describe the result you need.</p></section>

            <Card className="border-slate-200 shadow-sm"><CardContent className="pt-6"><NewWorkForm projects={data.projects.map((project) => ({ id: project.project_id, name: project.project_name }))} /></CardContent></Card>
          </div>
        </section>
      </div>
    </main>
  );
}
