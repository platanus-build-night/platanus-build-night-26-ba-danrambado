import { Badge } from "@/components/ui/badge";

export function NetworkBadge({ connectionCount }: { connectionCount: number }) {
  if (connectionCount === 0) return null;

  return (
    <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
      {connectionCount} connection{connectionCount !== 1 ? "s" : ""}
    </Badge>
  );
}
