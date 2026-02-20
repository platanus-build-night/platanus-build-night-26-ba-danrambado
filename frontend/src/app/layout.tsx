import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { CurrentUserProvider } from "@/hooks/use-current-user";
import { UserPicker } from "@/components/user-picker";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Serendip Lab",
  description: "AI-powered intentional connections",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}>
        <CurrentUserProvider>
          <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
              <div className="flex items-center gap-8">
                <Link href="/" className="text-xl font-bold tracking-tight">
                  Serendip Lab
                </Link>
                <nav className="hidden md:flex items-center gap-6 text-sm">
                  <Link href="/profiles" className="text-muted-foreground hover:text-foreground transition-colors">
                    People
                  </Link>
                  <Link href="/opportunities" className="text-muted-foreground hover:text-foreground transition-colors">
                    Opportunities
                  </Link>
                  <Link href="/opportunities/new" className="text-muted-foreground hover:text-foreground transition-colors">
                    Post Opportunity
                  </Link>
                </nav>
              </div>
              <UserPicker />
            </div>
          </header>
          <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
        </CurrentUserProvider>
      </body>
    </html>
  );
}
