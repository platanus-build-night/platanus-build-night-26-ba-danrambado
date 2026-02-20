"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import type { User } from "@/lib/types";
import { api } from "@/lib/api";

interface AuthContextValue {
  currentUser: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    name: string;
    email: string;
    password: string;
    bio: string;
    skills: string[];
    interests: string[];
    open_to: string[];
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  currentUser: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

const PUBLIC_PATHS = ["/", "/login", "/register"];

export function CurrentUserProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = localStorage.getItem("serendip_token");
    if (!token) {
      setLoading(false);
      if (!PUBLIC_PATHS.includes(pathname)) {
        router.replace("/login");
      }
      return;
    }
    api.auth
      .me()
      .then((user) => {
        setCurrentUser(user);
        setLoading(false);
      })
      .catch(() => {
        localStorage.removeItem("serendip_token");
        setLoading(false);
        if (!PUBLIC_PATHS.includes(pathname)) {
          router.replace("/login");
        }
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.auth.login(email, password);
    localStorage.setItem("serendip_token", res.token);
    setCurrentUser(res.user);
    router.push("/opportunities");
  }, [router]);

  const register = useCallback(
    async (data: {
      name: string;
      email: string;
      password: string;
      bio: string;
      skills: string[];
      interests: string[];
      open_to: string[];
    }) => {
      const res = await api.auth.register(data);
      localStorage.setItem("serendip_token", res.token);
      setCurrentUser(res.user);
      router.push("/opportunities");
    },
    [router]
  );

  const logout = useCallback(() => {
    api.auth.logout().catch(() => {});
    localStorage.removeItem("serendip_token");
    setCurrentUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ currentUser, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useCurrentUser() {
  return useContext(AuthContext);
}
