import { AppShell } from "@/components/app-shell";
import { StatGrid } from "@/components/stat-grid";
import { apiGetServer, type Me, type Overview } from "@/lib/server-api";

export default async function DashboardPage() {
  const [me, overview] = await Promise.all([
    apiGetServer<Me>("/auth/me"),
    apiGetServer<Overview>("/api/v1/overview")
  ]);

  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {me.email} · Tenant {me.azure_tenant_id}
        </p>
      </div>
      <StatGrid overview={overview} />
    </AppShell>
  );
}
