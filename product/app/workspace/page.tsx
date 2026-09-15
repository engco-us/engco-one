import { Card, CardContent } from '@/components/ui/card';
import { getWorkspaceSnapshot } from '@/lib/engco/data';
import { NewWorkForm } from './new-work-form';

export default async function WorkspacePage() {
  const data = await getWorkspaceSnapshot();

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 pt-16 lg:pt-24">
      <h1 className="text-3xl font-semibold tracking-tight">Quantity takeoff</h1>
      <Card className="border-slate-200 shadow-sm">
        <CardContent className="pt-6">
          <NewWorkForm projects={data.projects.map((project) => ({ id: project.project_id, name: project.project_name }))} />
        </CardContent>
      </Card>
    </div>
  );
}
