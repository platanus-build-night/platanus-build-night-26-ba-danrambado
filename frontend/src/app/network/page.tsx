"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { ConnectionRequest, LayeredNetwork, SearchResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { RequestCard } from "@/components/request-card";
import { ProfileCard } from "@/components/profile-card";

const DEGREE_BADGE: Record<string, string> = {
  "1st": "bg-green-100 text-green-800",
  "2nd": "bg-blue-100 text-blue-800",
  other: "bg-gray-100 text-gray-800",
};

export default function NetworkPage() {
  const [network, setNetwork] = useState<LayeredNetwork | null>(null);
  const [incoming, setIncoming] = useState<ConnectionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);

  const loadData = useCallback(() => {
    Promise.all([api.users.myNetwork(), api.connectionRequests.incoming()])
      .then(([net, reqs]) => {
        setNetwork(net);
        setIncoming(reqs);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    const timeout = setTimeout(() => {
      setSearching(true);
      api.users
        .search(searchQuery.trim())
        .then(setSearchResults)
        .catch(() => setSearchResults([]))
        .finally(() => setSearching(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-12 rounded-lg bg-muted animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-48 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Network</h1>
        <p className="text-muted-foreground mt-1">
          Your connections and people you can discover
        </p>
      </div>

      <Input
        placeholder="Search people by name, skills, or interests..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="max-w-md"
      />

      {searchResults !== null ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Search results {searching && "(searching...)"}
            </h2>
            <button
              onClick={() => setSearchQuery("")}
              className="text-sm text-purple-600 hover:underline"
            >
              Clear search
            </button>
          </div>
          {searchResults.length === 0 ? (
            <p className="text-muted-foreground text-sm">No results found.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((r) => (
                <Link key={r.user.id} href={`/profiles/${r.user.id}`} className="block">
                  <Card className="h-full hover:bg-muted/50 transition-colors">
                    <CardContent className="pt-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold">
                            {r.user.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </div>
                          <div>
                            <p className="font-medium text-sm">{r.user.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {r.user.connection_count} connections
                            </p>
                          </div>
                        </div>
                        <Badge className={DEGREE_BADGE[r.degree] ?? DEGREE_BADGE.other}>
                          {r.degree === "other" ? "Discover" : r.degree}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">{r.user.bio}</p>
                      {r.shared_connections.length > 0 && (
                        <p className="text-xs text-blue-600">
                          Connected through {r.shared_connections.join(", ")}
                        </p>
                      )}
                      <div className="flex flex-wrap gap-1">
                        {r.user.skills.slice(0, 3).map((s) => (
                          <Badge key={s} variant="secondary" className="text-xs">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      ) : (
        <>
          {incoming.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">
                Incoming Requests ({incoming.length})
              </h2>
              <div className="space-y-2">
                {incoming.map((req) => (
                  <RequestCard key={req.id} request={req} type="incoming" onAction={loadData} />
                ))}
              </div>
              <Separator />
            </div>
          )}

          {network && (
            <>
              <div className="space-y-4">
                <h2 className="text-lg font-semibold">
                  Direct Connections ({network.first_degree.length})
                </h2>
                {network.first_degree.length === 0 ? (
                  <p className="text-muted-foreground text-sm">
                    No connections yet. Post an opportunity or search for people to connect with.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {network.first_degree.map((m) => (
                      <ProfileCard key={m.user.id} user={m.user} />
                    ))}
                  </div>
                )}
              </div>

              {network.second_degree.length > 0 && (
                <>
                  <Separator />
                  <div className="space-y-4">
                    <h2 className="text-lg font-semibold">
                      2nd Degree ({network.second_degree.length})
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {network.second_degree.map((m) => (
                        <div key={m.user.id} className="relative">
                          <ProfileCard user={m.user} />
                          {m.shared_connections.length > 0 && (
                            <p className="text-xs text-blue-600 mt-1 px-1">
                              Through {m.shared_connections.join(", ")}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
