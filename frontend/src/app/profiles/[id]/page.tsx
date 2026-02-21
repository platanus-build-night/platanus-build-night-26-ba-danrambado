"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { User, NetworkData, Impression } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { FeedbackForm } from "@/components/feedback-form";
import { useCurrentUser } from "@/hooks/use-current-user";

export default function ProfileDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { currentUser } = useCurrentUser();
  const [user, setUser] = useState<User | null>(null);
  const [network, setNetwork] = useState<NetworkData | null>(null);
  const [impression, setImpression] = useState<Impression | null>(null);
  const [loading, setLoading] = useState(true);
  const [canLeaveFeedback, setCanLeaveFeedback] = useState(false);

  const loadImpression = useCallback(() => {
    api.users.impression(id).then(setImpression).catch(() => {});
  }, [id]);

  useEffect(() => {
    Promise.all([api.users.get(id), api.users.network(id)]).then(([u, n]) => {
      setUser(u);
      setNetwork(n);
      setLoading(false);
    });
    loadImpression();
  }, [id, loadImpression]);

  useEffect(() => {
    if (currentUser && currentUser.id !== id) {
      api.feedback.canLeave(id).then((r) => setCanLeaveFeedback(r.allowed)).catch(() => {});
    }
  }, [currentUser, id]);

  if (loading || !user) {
    return <div className="h-96 rounded-lg bg-muted animate-pulse" />;
  }

  const isOwnProfile = currentUser?.id === user.id;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{user.name}</h1>
        <p className="text-muted-foreground mt-2 text-lg">{user.bio}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {user.skills.map((s) => (
                <Badge key={s} variant="secondary">
                  {s}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Interests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {user.interests.map((i) => (
                <Badge key={i} variant="outline">
                  {i}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Open to</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {user.open_to.map((o) => (
              <Badge key={o} className="capitalize">
                {o}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Community Impression */}
      <Separator />
      <div>
        <h2 className="text-xl font-semibold mb-4">Community Impression</h2>
        {impression && impression.feedback_count > 0 ? (
          <Card className="border-purple-200 bg-purple-50/50">
            <CardContent className="pt-6 space-y-3">
              <p className="text-sm leading-relaxed">{impression.summary}</p>
              {Object.keys(impression.by_context).length > 0 && (
                <div className="space-y-2 pt-2">
                  {Object.entries(impression.by_context).map(([ctx, text]) => (
                    <div key={ctx} className="flex gap-2">
                      <Badge variant="outline" className="capitalize shrink-0">
                        {ctx}
                      </Badge>
                      <span className="text-sm text-muted-foreground">{text}</span>
                    </div>
                  ))}
                </div>
              )}
              <p className="text-xs text-muted-foreground pt-1">
                Based on {impression.feedback_count} anonymous community interaction
                {impression.feedback_count !== 1 ? "s" : ""}
              </p>
            </CardContent>
          </Card>
        ) : (
          <p className="text-muted-foreground text-sm">No community feedback yet.</p>
        )}
      </div>

      {/* Feedback Form */}
      {currentUser && !isOwnProfile && (
        <>
          <Separator />
          {canLeaveFeedback ? (
            <FeedbackForm toUserId={user.id} onSubmitted={loadImpression} />
          ) : (
            <p className="text-sm text-muted-foreground">
              You can leave feedback after completing an interaction with this person.
            </p>
          )}
        </>
      )}

      {network && network.connections.length > 0 && (
        <>
          <Separator />
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Connections ({network.connections.length})
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {network.connections.map((conn) => (
                <Link
                  key={conn.id}
                  href={`/profiles/${conn.user_id}`}
                  className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold">
                    {conn.user_name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <div className="font-medium text-sm">{conn.user_name}</div>
                    <div className="text-xs text-muted-foreground capitalize">{conn.source}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
