export type Me = {
  user_id: string;
  tenant_id: string;
  azure_tenant_id: string;
  email: string;
};

export type Overview = {
  subscriptions: number;
  resources: number;
  virtual_machines: number;
  storage_accounts: number;
  aks_clusters: number;
  key_vaults: number;
};

export type Subscription = {
  id: string;
  subscription_id: string;
  display_name: string;
  state: string;
  authorization_source?: string | null;
};

export type AzureResource = {
  id: string;
  azure_resource_id: string;
  name: string;
  resource_type: string;
  resource_group?: string | null;
  location?: string | null;
  tags: Record<string, string>;
  properties: Record<string, unknown>;
  updated_at: string;
};

const browserBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const serverBase = process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function apiBase() {
  return typeof window === "undefined" ? serverBase : browserBase;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBase()}${path}`, {
    credentials: "include",
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function startLogin(): Promise<void> {
  const response = await apiGet<{ authorization_url: string }>("/auth/login");
  window.location.assign(response.authorization_url);
}

export async function logout(): Promise<void> {
  await fetch(`${apiBase()}/auth/logout`, { method: "POST", credentials: "include" });
  window.location.assign("/login");
}
