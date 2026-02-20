"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/use-current-user";

export default function Home() {
  const { currentUser, loading } = useCurrentUser();
  const router = useRouter();

  useEffect(() => {
    if (!loading && currentUser) {
      router.replace("/opportunities");
    }
  }, [loading, currentUser, router]);

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
    </div>
  );
}
