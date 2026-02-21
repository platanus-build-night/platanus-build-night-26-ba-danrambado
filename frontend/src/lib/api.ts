import type {
  AuthResponse,
  ConnectionRequest,
  Impression,
  LayeredNetwork,
  NetworkData,
  Opportunity,
  OpportunityDetail,
  SearchResult,
  User,
} from "./types";

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
    myNetwork: () => fetcher<LayeredNetwork>("/users/network/me"),
    search: (q: string) => fetcher<SearchResult[]>(`/users/search?q=${encodeURIComponent(q)}`),
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
    canLeave: (userId: string) =>
      fetcher<{ allowed: boolean }>(`/feedback/can-leave/${userId}`),
    experiences: (toUserId: string) =>
      fetcher<{ experiences: Array<{ opportunity_id: string; opportunity_type: string; opportunity_title: string }> }>(
        `/feedback/experiences/${toUserId}`
      ),
  },
  connectionRequests: {
    create: (data: { to_user_id: string; opportunity_id: string; match_id?: string }) =>
      fetcher<ConnectionRequest>("/connection-requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    check: (opportunityId: string, toUserId: string) =>
      fetcher<{ exists: boolean }>(`/connection-requests/check?opportunity_id=${encodeURIComponent(opportunityId)}&to_user_id=${encodeURIComponent(toUserId)}`),
    incoming: () => fetcher<ConnectionRequest[]>("/connection-requests/incoming"),
    outgoing: () => fetcher<ConnectionRequest[]>("/connection-requests/outgoing"),
    byOpportunity: (opportunityId: string) =>
      fetcher<ConnectionRequest[]>(`/connection-requests/by-opportunity/${opportunityId}`),
    accept: (id: string) =>
      fetcher<ConnectionRequest>(`/connection-requests/${id}/accept`, { method: "POST" }),
    decline: (id: string) =>
      fetcher<ConnectionRequest>(`/connection-requests/${id}/decline`, { method: "POST" }),
  },
};
