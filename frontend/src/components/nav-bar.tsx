"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useCurrentUser } from "@/hooks/use-current-user";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function NavBar() {
  const { currentUser, loading, logout } = useCurrentUser();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    if (!currentUser) return;
    api.connectionRequests
      .incoming()
      .then((reqs) => setPendingCount(reqs.length))
      .catch(() => {});
  }, [currentUser]);

  return (
    <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold tracking-tight">
            Serendip Lab
          </Link>
          {currentUser && (
            <nav className="hidden md:flex items-center gap-6 text-sm">
              <Link
                href={`/profiles/${currentUser.id}`}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                My Profile
              </Link>
              <Link
                href="/network"
                className="text-muted-foreground hover:text-foreground transition-colors relative"
              >
                My Network
                {pendingCount > 0 && (
                  <span className="absolute -top-2 -right-4 bg-red-500 text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                    {pendingCount}
                  </span>
                )}
              </Link>
              <Link
                href="/opportunities"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Opportunities
              </Link>
              <Link
                href="/opportunities/new"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Post Opportunity
              </Link>
            </nav>
          )}
        </div>

        {!loading && (
          <div className="flex items-center gap-3">
            {currentUser ? (
              <>
                <span className="text-sm text-muted-foreground hidden sm:inline">
                  {currentUser.name}
                </span>
                <Button variant="outline" size="sm" onClick={logout}>
                  Log out
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Log in
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Sign up</Button>
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
