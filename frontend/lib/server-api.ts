import { cookies } from "next/headers";
import type { AzureResource, Me, Overview, Subscription } from "@/lib/api";

const serverBase = process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function apiGetServer<T>(path: string): Promise<T> {
  const cookieHeader = (await cookies()).toString();
  const response = await fetch(`${serverBase}${path}`, {
    cache: "no-store",
    headers: {
      cookie: cookieHeader
    }
  });
  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export type { AzureResource, Me, Overview, Subscription };
