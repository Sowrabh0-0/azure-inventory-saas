import { AppShell } from "@/components/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiGetServer, type Me } from "@/lib/server-api";

export default async function SettingsPage() {
  const me = await apiGetServer<Me>("/auth/me");

  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">Tenant and session details</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Current identity</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm">
          <div>
            <span className="text-muted-foreground">Email</span>
            <div className="font-medium">{me.email}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Azure tenant</span>
            <div className="font-medium">{me.azure_tenant_id}</div>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
