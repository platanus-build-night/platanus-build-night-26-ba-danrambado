export interface User {
  id: string;
  name: string;
  email: string;
  bio: string;
  skills: string[];
  interests: string[];
  open_to: string[];
  created_at: string;
  connection_count: number;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Impression {
  summary: string;
  by_context: Record<string, string>;
  feedback_count: number;
}

export interface Opportunity {
  id: string;
  title: string;
  description: string;
  type: string;
  posted_by: string;
  poster_name: string;
  created_at: string;
}

export interface Match {
  id: string;
  opportunity_id: string;
  user_id: string;
  user_name: string;
  user_bio: string;
  user_skills: string[];
  score: number;
  embedding_score: number;
  network_score: number;
  explanation: string;
  rank: number;
  created_at: string;
}

export interface OpportunityDetail {
  opportunity: Opportunity;
  matches: Match[];
}

export interface Connection {
  id: string;
  user_id: string;
  user_name: string;
  source: string;
  strength: number;
}

export interface NetworkData {
  user: User;
  connections: Connection[];
}

export interface ConnectionRequest {
  id: string;
  from_user_id: string;
  to_user_id: string;
  opportunity_id: string;
  match_id: string;
  status: string;
  from_user_name: string;
  to_user_name: string;
  opportunity_title: string;
  created_at: string;
}

export interface NetworkMember {
  user: User;
  degree: number;
  shared_connections: string[];
  connection_source: string;
}

export interface LayeredNetwork {
  first_degree: NetworkMember[];
  second_degree: NetworkMember[];
  pending_incoming: number;
}

export interface SearchResult {
  user: User;
  degree: string;
  shared_connections: string[];
}

export const OPPORTUNITY_TYPES = [
  { value: "job", label: "Job" },
  { value: "project", label: "Project" },
  { value: "help", label: "Help" },
  { value: "collab", label: "Collaboration" },
  { value: "date", label: "Date" },
  { value: "fun", label: "Fun" },
] as const;

export const TYPE_COLORS: Record<string, string> = {
  job: "bg-blue-100 text-blue-800",
  project: "bg-purple-100 text-purple-800",
  help: "bg-amber-100 text-amber-800",
  collab: "bg-green-100 text-green-800",
  date: "bg-pink-100 text-pink-800",
  fun: "bg-orange-100 text-orange-800",
};
