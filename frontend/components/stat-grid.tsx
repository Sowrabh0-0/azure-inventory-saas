import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Overview } from "@/lib/api";

const labels: Array<[keyof Overview, string]> = [
  ["subscriptions", "Subscriptions"],
  ["resources", "Resources"],
  ["virtual_machines", "Virtual machines"],
  ["storage_accounts", "Storage accounts"],
  ["aks_clusters", "AKS clusters"],
  ["key_vaults", "Key Vaults"]
];

export function StatGrid({ overview }: { overview: Overview }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {labels.map(([key, label]) => (
        <Card key={key}>
          <CardHeader>
            <CardTitle>{label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">{overview[key]}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

