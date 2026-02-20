import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Opportunity } from "@/lib/types";
import { TYPE_COLORS } from "@/lib/types";

export function OpportunityCard({ opportunity }: { opportunity: Opportunity }) {
  const colorClass = TYPE_COLORS[opportunity.type] ?? "bg-gray-100 text-gray-800";

  return (
    <Link href={`/opportunities/${opportunity.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md cursor-pointer">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg leading-snug">{opportunity.title}</CardTitle>
            <Badge className={`shrink-0 ${colorClass}`}>{opportunity.type}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground line-clamp-3">{opportunity.description}</p>
          <p className="text-xs text-muted-foreground">
            Posted by <span className="font-medium text-foreground">{opportunity.poster_name}</span>
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
