'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot, ClipboardCheck, FolderKanban, ListTodo, Radar, Settings } from 'lucide-react';

const nav = [
  { href: '/workspace', label: 'New Work', icon: ListTodo, exact: true },
  { href: '/workspace/projects', label: 'Projects', icon: FolderKanban, exact: false },
  { href: '/workspace/agents', label: 'Agents', icon: Bot, exact: false },
  { href: '/workspace/scorecard', label: 'Scorecard', icon: ClipboardCheck, exact: false },
  { href: '/workspace/qa', label: 'Design QA', icon: ClipboardCheck, exact: false },
  { href: '/workspace/leads', label: 'Leads Finder', icon: Radar, exact: false },
  { href: '/dashboard', label: 'Team Settings', icon: Settings, exact: false },
] as const;

export function WorkspaceNav() {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {nav.map(({ href, label, icon: Icon, exact }) => {
        const isActive = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link key={href} href={href}>
            <span
              className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm ${
                isActive ? 'bg-slate-800 text-white font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className="h-4 w-4" /> {label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
