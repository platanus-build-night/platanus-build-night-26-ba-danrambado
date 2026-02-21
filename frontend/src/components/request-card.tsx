"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { ConnectionRequest } from "@/lib/types";
import { api } from "@/lib/api";

interface RequestCardProps {
  request: ConnectionRequest;
  type: "incoming" | "outgoing";
  onAction?: () => void;
}

export function RequestCard({ request, type, onAction }: RequestCardProps) {
  const [status, setStatus] = useState(request.status);
  const [acting, setActing] = useState(false);

  async function handleAccept() {
    setActing(true);
    try {
      await api.connectionRequests.accept(request.id);
      setStatus("accepted");
      onAction?.();
    } catch {
      setActing(false);
    }
  }

  async function handleDecline() {
    setActing(true);
    try {
      await api.connectionRequests.decline(request.id);
      setStatus("declined");
      onAction?.();
    } catch {
      setActing(false);
    }
  }

  const otherName = type === "incoming" ? request.from_user_name : request.to_user_name;
  const otherId = type === "incoming" ? request.from_user_id : request.to_user_id;

  return (
    <Card>
      <CardContent className="pt-4 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold shrink-0">
            {otherName
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
          <div className="flex-1 min-w-0">
            <Link href={`/profiles/${otherId}`} className="font-medium text-sm hover:underline">
              {otherName}
            </Link>
            <p className="text-xs text-muted-foreground line-clamp-1">
              {type === "incoming" ? "wants to connect" : "request sent"} via{" "}
              <Link
                href={`/opportunities/${request.opportunity_id}`}
                className="font-medium text-foreground hover:underline"
              >
                {request.opportunity_title}
              </Link>
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {status === "pending" && type === "incoming" && (
              <>
                <Button size="sm" onClick={handleAccept} disabled={acting}>
                  Accept
                </Button>
                <Button size="sm" variant="outline" onClick={handleDecline} disabled={acting}>
                  Decline
                </Button>
              </>
            )}
            {status === "accepted" && (
              <span className="text-xs text-green-600 font-medium">Connected</span>
            )}
            {status === "declined" && (
              <span className="text-xs text-muted-foreground">Declined</span>
            )}
            {status === "pending" && type === "outgoing" && (
              <span className="text-xs text-amber-600 font-medium">Pending</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
