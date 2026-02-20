import type { User, Opportunity, OpportunityDetail, NetworkData } from "./types";

const BASE = "/api";

async function fetcher<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export const api = {
  users: {
    list: () => fetcher<User[]>("/users"),
    get: (id: string) => fetcher<User>(`/users/${id}`),
    network: (id: string) => fetcher<NetworkData>(`/users/${id}/network`),
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
};
