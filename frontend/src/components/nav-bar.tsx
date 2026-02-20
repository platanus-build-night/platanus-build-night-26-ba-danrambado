"use client";

import Link from "next/link";
import { useCurrentUser } from "@/hooks/use-current-user";
import { Button } from "@/components/ui/button";

export function NavBar() {
  const { currentUser, loading, logout } = useCurrentUser();

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
                href="/profiles"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                People
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
