"use client";

import { useCurrentUser } from "@/hooks/use-current-user";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function UserPicker() {
  const { currentUser, setCurrentUser, users } = useCurrentUser();

  return (
    <Select
      value={currentUser?.id ?? ""}
      onValueChange={(id) => {
        const user = users.find((u) => u.id === id) ?? null;
        setCurrentUser(user);
      }}
    >
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Act as user..." />
      </SelectTrigger>
      <SelectContent>
        {users.map((u) => (
          <SelectItem key={u.id} value={u.id}>
            {u.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
