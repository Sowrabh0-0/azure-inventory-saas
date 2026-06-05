import { AppShell } from "@/components/app-shell";
import { apiGetServer, type Subscription } from "@/lib/server-api";

export default async function SubscriptionsPage() {
  const subscriptions = await apiGetServer<Subscription[]>("/api/v1/subscriptions");

  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Subscriptions</h1>
        <p className="mt-1 text-sm text-muted-foreground">{subscriptions.length} tenant-scoped subscriptions</p>
      </div>
      <div className="overflow-hidden rounded-lg border border-border bg-card">
        <table className="w-full text-left text-sm">
          <thead className="bg-muted text-muted-foreground">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Subscription ID</th>
              <th className="px-4 py-3 font-medium">State</th>
            </tr>
          </thead>
          <tbody>
            {subscriptions.map((subscription) => (
              <tr key={subscription.id} className="border-t border-border">
                <td className="px-4 py-3 font-medium">{subscription.display_name}</td>
                <td className="px-4 py-3 text-muted-foreground">{subscription.subscription_id}</td>
                <td className="px-4 py-3">{subscription.state}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
