import { getProjects } from '@/lib/engco/data';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { NewProjectForm } from './new-project-form';

export default async function ProjectsPage() {
  const projects = await getProjects();

  return (
    <div className="mx-auto max-w-5xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">PROJECTS</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Registered projects</h1>
        <p className="mt-3 text-muted-foreground">Real rows from data/project_registry.json — registering here runs SOP-001 for real.</p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2">
        {projects.map((p) => (
          <Card key={p.project_id}>
            <CardHeader><CardTitle className="text-base">{p.project_name}</CardTitle></CardHeader>
            <CardContent className="space-y-1 text-sm">
              <p className="font-mono text-xs text-muted-foreground">{p.project_id}</p>
              <p>{p.city}</p>
              <div className="flex items-center gap-2 pt-1">
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium">{p.current_phase}</span>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">{p.overall_status}</span>
              </div>
            </CardContent>
          </Card>
        ))}
        {!projects.length && <p className="text-sm text-muted-foreground">No projects registered yet.</p>}
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader><CardTitle>Register a new project</CardTitle></CardHeader>
        <CardContent><NewProjectForm /></CardContent>
      </Card>
    </div>
  );
}
