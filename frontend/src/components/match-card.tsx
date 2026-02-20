"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Match, Impression } from "@/lib/types";
import { api } from "@/lib/api";

interface MatchCardProps {
  match: Match;
  rank: number;
  showConnect?: boolean;
  opportunityId?: string;
}

export function MatchCard({ match, rank, showConnect, opportunityId }: MatchCardProps) {
  const scorePercent = Math.round(match.score * 100);
  const embeddingPercent = Math.round(match.embedding_score * 100);
  const hasNetworkBoost = match.network_score > 0;
  const [impression, setImpression] = useState<Impression | null>(null);
  const [connectStatus, setConnectStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  useEffect(() => {
    api.users.impression(match.user_id).then(setImpression).catch(() => {});
  }, [match.user_id]);

  const snippetText =
    impression && impression.feedback_count > 0 && impression.summary
      ? impression.summary.length > 120
        ? impression.summary.slice(0, 120) + "..."
        : impression.summary
      : null;

  async function handleConnect() {
    if (!opportunityId) return;
    setConnectStatus("sending");
    try {
      await api.connectionRequests.create({
        to_user_id: match.user_id,
        opportunity_id: opportunityId,
        match_id: match.id,
      });
      setConnectStatus("sent");
    } catch {
      setConnectStatus("error");
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
            {rank}
          </div>
          <div className="flex-1 min-w-0">
            <Link
              href={`/profiles/${match.user_id}`}
              className="font-semibold hover:underline text-base"
            >
              {match.user_name}
            </Link>
            <p className="text-xs text-muted-foreground line-clamp-1">{match.user_bio}</p>
          </div>
          <div className="text-right shrink-0">
            <div className="text-2xl font-bold">{scorePercent}%</div>
            <div className="text-xs text-muted-foreground">match</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm leading-relaxed">{match.explanation}</p>

        {snippetText && (
          <div className="rounded-md bg-purple-50 border border-purple-200 px-3 py-2">
            <p className="text-xs font-medium text-purple-700 mb-0.5">Community impression</p>
            <p className="text-xs text-purple-600">{snippetText}</p>
          </div>
        )}

        <div className="flex flex-wrap gap-1.5">
          {match.user_skills.slice(0, 5).map((s) => (
            <Badge key={s} variant="secondary" className="text-xs">
              {s}
            </Badge>
          ))}
        </div>
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>Skill fit: {embeddingPercent}%</span>
            {hasNetworkBoost && (
              <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                Network boost +{Math.round(match.network_score * 100)}%
              </Badge>
            )}
          </div>
          {showConnect && (
            <Button
              size="sm"
              variant={connectStatus === "sent" ? "outline" : "default"}
              disabled={connectStatus === "sending" || connectStatus === "sent"}
              onClick={handleConnect}
            >
              {connectStatus === "idle" && "Connect"}
              {connectStatus === "sending" && "Sending..."}
              {connectStatus === "sent" && "Request sent"}
              {connectStatus === "error" && "Try again"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
