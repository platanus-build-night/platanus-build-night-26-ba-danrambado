"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { OpportunityDetail } from "@/lib/types";
import { TYPE_COLORS } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { MatchCard } from "@/components/match-card";
import { useCurrentUser } from "@/hooks/use-current-user";

export default function OpportunityDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { currentUser } = useCurrentUser();
  const [data, setData] = useState<OpportunityDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.opportunities.get(id).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [id]);

  if (loading || !data) {
    return (
      <div className="space-y-4">
        <div className="h-32 rounded-lg bg-muted animate-pulse" />
        <div className="h-48 rounded-lg bg-muted animate-pulse" />
        <div className="h-48 rounded-lg bg-muted animate-pulse" />
      </div>
    );
  }

  const { opportunity, matches } = data;
  const colorClass = TYPE_COLORS[opportunity.type] ?? "bg-gray-100 text-gray-800";
  const isOwner = currentUser?.id === opportunity.posted_by;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-1">
              <CardTitle className="text-2xl">{opportunity.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                Posted by{" "}
                <Link
                  href={`/profiles/${opportunity.posted_by}`}
                  className="font-medium text-foreground hover:underline"
                >
                  {opportunity.poster_name}
                </Link>
              </p>
            </div>
            <Badge className={colorClass}>{opportunity.type}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground whitespace-pre-wrap">{opportunity.description}</p>
        </CardContent>
      </Card>

      {isOwner && (
        <>
          <Separator />

          <div>
            <h2 className="text-xl font-semibold mb-1">
              AI Matches ({matches.length})
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Ranked by skill fit and network proximity
            </p>

            {matches.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground">No matches found for this opportunity.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {matches.map((m) => (
                  <MatchCard
                    key={m.id}
                    match={m}
                    rank={m.rank}
                    showConnect
                    opportunityId={opportunity.id}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
