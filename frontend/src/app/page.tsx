"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useCurrentUser } from "@/hooks/use-current-user";
import { api } from "@/lib/api";

export default function Home() {
  const { currentUser, loading } = useCurrentUser();
  const router = useRouter();
  const [userCount, setUserCount] = useState(0);
  const [oppCount, setOppCount] = useState(0);

  useEffect(() => {
    if (!loading && currentUser) {
      router.replace("/opportunities");
    }
  }, [loading, currentUser, router]);

  useEffect(() => {
    api.users.list().then((u) => setUserCount(u.length)).catch(() => {});
    api.opportunities.list().then((o) => setOppCount(o.length)).catch(() => {});
  }, []);

  if (loading || currentUser) return null;

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center space-y-8">
      <div className="space-y-4 max-w-2xl">
        <h1 className="text-5xl font-bold tracking-tight">
          Turn random luck into
          <br />
          <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            intentional connections
          </span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto">
          Serendip Lab uses AI to match people with the right opportunities, collaborations, and
          connections. Stop searching. Start connecting.
        </p>
      </div>

      <div className="flex gap-4">
        <Link href="/register">
          <Button size="lg">Get Started</Button>
        </Link>
        <Link href="/login">
          <Button size="lg" variant="outline">
            Log In
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-6 pt-8 w-full max-w-lg">
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-3xl font-bold">{userCount}</div>
            <div className="text-sm text-muted-foreground">People</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-3xl font-bold">{oppCount}</div>
            <div className="text-sm text-muted-foreground">Opportunities</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-3xl font-bold">AI</div>
            <div className="text-sm text-muted-foreground">Matching</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
