import { AppShell } from "@/components/app-shell";
import { ResourceTable } from "@/components/resource-table";
import { apiGetServer, type AzureResource } from "@/lib/server-api";

export default async function ResourcesPage() {
  const resources = await apiGetServer<AzureResource[]>("/api/v1/resources");

  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Resources</h1>
        <p className="mt-1 text-sm text-muted-foreground">{resources.length} indexed Azure resources</p>
      </div>
      <ResourceTable resources={resources} />
    </AppShell>
  );
}
