import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { User } from "@/lib/types";

export function ProfileCard({ user }: { user: User }) {
  return (
    <Link href={`/profiles/${user.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md cursor-pointer">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{user.name}</CardTitle>
            {user.connection_count > 0 && (
              <span className="text-xs text-muted-foreground">
                {user.connection_count} connection{user.connection_count !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground line-clamp-2">{user.bio}</p>
          <div className="flex flex-wrap gap-1">
            {user.skills.slice(0, 4).map((s) => (
              <Badge key={s} variant="secondary" className="text-xs">
                {s}
              </Badge>
            ))}
            {user.skills.length > 4 && (
              <Badge variant="outline" className="text-xs">
                +{user.skills.length - 4}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap gap-1">
            {user.open_to.map((o) => (
              <Badge key={o} variant="outline" className="text-xs capitalize">
                {o}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
