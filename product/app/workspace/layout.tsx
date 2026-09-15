import Link from 'next/link';
import { WorkspaceNav } from './workspace-nav';

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <div className="mx-auto grid min-h-screen max-w-[1600px] md:grid-cols-[240px_1fr]">
        <aside className="hidden border-r bg-slate-950 p-5 text-slate-100 md:flex md:flex-col">
          <Link href="/workspace" className="mb-8 flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-lg bg-emerald-500 font-bold text-slate-950">E1</span>
            <span><strong className="block">ENGCO ONE</strong><small className="text-slate-400">Operations workspace</small></span>
          </Link>
          <WorkspaceNav />
        </aside>
        <section className="min-w-0">{children}</section>
      </div>
    </main>
  );
}
