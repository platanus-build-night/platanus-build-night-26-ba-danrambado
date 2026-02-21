"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { ConnectionRequest, OpportunityDetail } from "@/lib/types";
import { TYPE_COLORS } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { MatchCard } from "@/components/match-card";
import { RequestCard } from "@/components/request-card";
import { useCurrentUser } from "@/hooks/use-current-user";

export default function OpportunityDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { currentUser } = useCurrentUser();
  const [data, setData] = useState<OpportunityDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [joinStatus, setJoinStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [joinRequests, setJoinRequests] = useState<ConnectionRequest[]>([]);

  useEffect(() => {
    api.opportunities.get(id).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [id]);

  const isOwner = currentUser?.id === data?.opportunity.posted_by;

  useEffect(() => {
    if (isOwner && id) {
      api.connectionRequests.byOpportunity(id).then(setJoinRequests).catch(() => {});
    }
  }, [isOwner, id]);

  useEffect(() => {
    if (!isOwner && currentUser && data) {
      api.connectionRequests
        .check(data.opportunity.id, data.opportunity.posted_by)
        .then((r) => { if (r.exists) setJoinStatus("sent"); })
        .catch(() => {});
    }
  }, [isOwner, currentUser, data]);

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

  async function handleJoin() {
    setJoinStatus("sending");
    try {
      await api.connectionRequests.create({
        to_user_id: opportunity.posted_by,
        opportunity_id: opportunity.id,
      });
      setJoinStatus("sent");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      setJoinStatus(msg.includes("already sent") ? "sent" : "error");
    }
  }

  function refreshJoinRequests() {
    api.connectionRequests.byOpportunity(id).then(setJoinRequests).catch(() => {});
  }

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

      {!isOwner && currentUser && (
        <div className="flex justify-center">
          <Button
            size="lg"
            variant={joinStatus === "sent" ? "outline" : "default"}
            disabled={joinStatus === "sending" || joinStatus === "sent"}
            onClick={handleJoin}
          >
            {joinStatus === "idle" && "Join this opportunity"}
            {joinStatus === "sending" && "Sending request..."}
            {joinStatus === "sent" && "Request sent"}
            {joinStatus === "error" && "Try again"}
          </Button>
        </div>
      )}

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

          {joinRequests.length > 0 && (
            <>
              <Separator />
              <div>
                <h2 className="text-xl font-semibold mb-1">
                  Join Requests ({joinRequests.length})
                </h2>
                <p className="text-sm text-muted-foreground mb-4">
                  People who want to join this opportunity
                </p>
                <div className="space-y-3">
                  {joinRequests.map((r) => (
                    <RequestCard key={r.id} request={r} type="incoming" onAction={refreshJoinRequests} />
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
