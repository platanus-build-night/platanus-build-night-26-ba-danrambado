"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Opportunity } from "@/lib/types";
import { OpportunityCard } from "@/components/opportunity-card";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/use-current-user";

export default function OpportunitiesPage() {
  const { currentUser } = useCurrentUser();
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.opportunities.list().then((data) => {
      setOpps(data);
      setLoading(false);
    });
  }, []);

  const myOpps = useMemo(
    () => (currentUser ? opps.filter((o) => o.posted_by === currentUser.id) : []),
    [opps, currentUser]
  );
  const otherOpps = useMemo(
    () => (currentUser ? opps.filter((o) => o.posted_by !== currentUser.id) : opps),
    [opps, currentUser]
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Opportunities</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Opportunities</h1>
          <p className="text-muted-foreground mt-1">{opps.length} active opportunities</p>
        </div>
        <Link href="/opportunities/new">
          <Button>Post Opportunity</Button>
        </Link>
      </div>

      {opps.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-muted-foreground text-lg">No opportunities yet.</p>
          <Link href="/opportunities/new">
            <Button className="mt-4">Be the first to post</Button>
          </Link>
        </div>
      ) : (
        <>
          {myOpps.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">My Opportunities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {myOpps.map((o) => (
                  <OpportunityCard key={o.id} opportunity={o} />
                ))}
              </div>
            </div>
          )}

          {otherOpps.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Explore Opportunities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {otherOpps.map((o) => (
                  <OpportunityCard key={o.id} opportunity={o} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
