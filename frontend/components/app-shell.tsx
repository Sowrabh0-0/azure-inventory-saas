"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Cloud, Database, LayoutDashboard, LogOut, Settings, ShieldCheck } from "lucide-react";
import { logout } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/subscriptions", label: "Subscriptions", icon: Cloud },
  { href: "/resources", label: "Resources", icon: Database },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-card md:block">
        <div className="flex h-16 items-center gap-2 border-b border-border px-5">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <span className="font-semibold">Azure Inventory</span>
        </div>
        <nav className="space-y-1 p-3">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground",
                  active && "bg-muted font-medium text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="md:pl-64">
        <header className="flex h-16 items-center justify-between border-b border-border bg-card px-5">
          <span className="text-sm font-medium">Tenant-scoped inventory</span>
          <Button variant="outline" onClick={() => void logout()}>
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </header>
        <div className="p-5">{children}</div>
      </main>
    </div>
  );
}

