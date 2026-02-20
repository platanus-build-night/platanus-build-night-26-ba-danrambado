import type { AuthResponse, Impression, NetworkData, Opportunity, OpportunityDetail, User } from "./types";

const BASE = "/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("serendip_token");
}

async function fetcher<T>(url: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE}${url}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      fetcher<AuthResponse>("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      }),
    register: (data: {
      name: string;
      email: string;
      password: string;
      bio: string;
      skills: string[];
      interests: string[];
      open_to: string[];
    }) =>
      fetcher<AuthResponse>("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    me: () => fetcher<User>("/auth/me"),
    logout: () => fetcher<void>("/auth/logout", { method: "POST" }),
  },
  users: {
    list: () => fetcher<User[]>("/users"),
    get: (id: string) => fetcher<User>(`/users/${id}`),
    network: (id: string) => fetcher<NetworkData>(`/users/${id}/network`),
    impression: (id: string) => fetcher<Impression>(`/users/${id}/impression`),
  },
  opportunities: {
    list: () => fetcher<Opportunity[]>("/opportunities"),
    get: (id: string) => fetcher<OpportunityDetail>(`/opportunities/${id}`),
    create: (data: { title: string; description: string; type: string; posted_by: string }) =>
      fetcher<OpportunityDetail>("/opportunities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
  },
  feedback: {
    create: (data: { to_user_id: string; opportunity_type: string; text: string }) =>
      fetcher<{ id: string }>("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
  },
};
