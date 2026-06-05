"use client";

import { ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { startLogin } from "@/lib/api";

export default function LoginPage() {
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
        <Button className="w-full" onClick={() => void startLogin()}>
          Continue with Microsoft
        </Button>
      </section>
    </main>
  );
}

