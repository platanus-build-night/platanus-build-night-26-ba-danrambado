"use client";

import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { User } from "@/lib/types";
import { api } from "@/lib/api";

interface CurrentUserContextValue {
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;
  users: User[];
  loading: boolean;
}

const CurrentUserContext = createContext<CurrentUserContextValue>({
  currentUser: null,
  setCurrentUser: () => {},
  users: [],
  loading: true,
});

export function CurrentUserProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.users.list().then((data) => {
      setUsers(data);
      const saved = localStorage.getItem("serendip_current_user");
      if (saved) {
        const found = data.find((u) => u.id === saved);
        if (found) setCurrentUser(found);
      }
      setLoading(false);
    });
  }, []);

  const handleSetUser = (user: User | null) => {
    setCurrentUser(user);
    if (user) {
      localStorage.setItem("serendip_current_user", user.id);
    } else {
      localStorage.removeItem("serendip_current_user");
    }
  };

  return (
    <CurrentUserContext.Provider value={{ currentUser, setCurrentUser: handleSetUser, users, loading }}>
      {children}
    </CurrentUserContext.Provider>
  );
}

export function useCurrentUser() {
  return useContext(CurrentUserContext);
}
