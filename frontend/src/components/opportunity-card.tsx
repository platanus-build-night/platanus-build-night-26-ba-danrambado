"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Opportunity } from "@/lib/types";
import { TYPE_COLORS } from "@/lib/types";
import { useCurrentUser } from "@/hooks/use-current-user";
import { api } from "@/lib/api";

export function OpportunityCard({ opportunity }: { opportunity: Opportunity }) {
  const { currentUser } = useCurrentUser();
  const colorClass = TYPE_COLORS[opportunity.type] ?? "bg-gray-100 text-gray-800";
  const isOwner = currentUser?.id === opportunity.posted_by;
  const [joinStatus, setJoinStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  useEffect(() => {
    if (!isOwner && currentUser) {
      api.connectionRequests
        .check(opportunity.id, opportunity.posted_by)
        .then((r) => { if (r.exists) setJoinStatus("sent"); })
        .catch(() => {});
    }
  }, [isOwner, currentUser, opportunity.id, opportunity.posted_by]);

  async function handleJoin(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
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

  return (
    <Link href={`/opportunities/${opportunity.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md cursor-pointer">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg leading-snug">{opportunity.title}</CardTitle>
            <Badge className={`shrink-0 ${colorClass}`}>{opportunity.type}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground line-clamp-3">{opportunity.description}</p>
          <div className="flex items-center justify-between pt-1">
            <p className="text-xs text-muted-foreground">
              Posted by <span className="font-medium text-foreground">{opportunity.poster_name}</span>
            </p>
            {!isOwner && currentUser && (
              <Button
                size="sm"
                variant={joinStatus === "sent" ? "outline" : "default"}
                disabled={joinStatus === "sending" || joinStatus === "sent"}
                onClick={handleJoin}
              >
                {joinStatus === "idle" && "Join"}
                {joinStatus === "sending" && "Sending..."}
                {joinStatus === "sent" && "Requested"}
                {joinStatus === "error" && "Try again"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
