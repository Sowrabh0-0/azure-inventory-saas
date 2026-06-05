"use client";

import { useState } from "react";
import { ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { startLogin } from "@/lib/api";

export default function LoginPage() {
  const [tenantId, setTenantId] = useState("");

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-6">
      <section className="w-full max-w-md rounded-lg border border-border bg-card p-8 shadow-sm">
        <div className="mb-8 flex items-center gap-3">
          <ShieldCheck className="h-7 w-7 text-primary" />
          <div>
            <h1 className="text-xl font-semibold">Azure Inventory</h1>
            <p className="text-sm text-muted-foreground">Sign in with Microsoft Entra ID</p>
          </div>
        </div>
        <label className="mb-2 block text-sm font-medium" htmlFor="tenant-id">
          Tenant ID
        </label>
        <input
          id="tenant-id"
          className="mb-4 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
          placeholder="Optional, e.g. 7f02300f-0f1b-4237-b981-c376377f394e"
          value={tenantId}
          onChange={(event) => setTenantId(event.target.value)}
        />
        <Button className="w-full" onClick={() => void startLogin(tenantId.trim() || undefined)}>
          Continue with Microsoft
        </Button>
      </section>
    </main>
  );
}
