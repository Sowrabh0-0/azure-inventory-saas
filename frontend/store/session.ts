"use client";

import { create } from "zustand";
import type { Me } from "@/lib/api";

type SessionState = {
  user: Me | null;
  setUser: (user: Me | null) => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  user: null,
  setUser: (user) => set({ user })
}));

