import type { AzureResource } from "@/lib/api";

export function ResourceTable({ resources }: { resources: AzureResource[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-muted text-muted-foreground">
          <tr>
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium">Type</th>
            <th className="px-4 py-3 font-medium">Resource group</th>
            <th className="px-4 py-3 font-medium">Location</th>
          </tr>
        </thead>
        <tbody>
          {resources.map((resource) => (
            <tr key={resource.id} className="border-t border-border">
              <td className="max-w-80 truncate px-4 py-3 font-medium">{resource.name}</td>
              <td className="px-4 py-3 text-muted-foreground">{resource.resource_type}</td>
              <td className="px-4 py-3">{resource.resource_group ?? "-"}</td>
              <td className="px-4 py-3">{resource.location ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

