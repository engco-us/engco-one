import { Card, CardContent } from '@/components/ui/card';
import { getWorkspaceSnapshot } from '@/lib/engco/data';
import { NewWorkForm } from './new-work-form';

export default async function WorkspacePage() {
  const data = await getWorkspaceSnapshot();

  return (
    <div className="mx-auto max-w-5xl space-y-7 p-5 pt-12 lg:p-12 lg:pt-20">
      <section>
        <p className="mb-2 text-sm font-medium text-emerald-700">NEW WORK</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">What needs to get done?</h1>
        <p className="mt-3 text-muted-foreground">Choose a project and describe the result you need.</p>
      </section>

      <Card className="border-slate-200 shadow-sm">
        <CardContent className="pt-6">
          <NewWorkForm projects={data.projects.map((project) => ({ id: project.project_id, name: project.project_name }))} />
        </CardContent>
      </Card>
    </div>
  );
}
