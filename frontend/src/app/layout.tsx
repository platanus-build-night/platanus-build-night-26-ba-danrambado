import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { CurrentUserProvider } from "@/hooks/use-current-user";
import { NavBar } from "@/components/nav-bar";

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
          <NavBar />
          <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
        </CurrentUserProvider>
      </body>
    </html>
  );
}
