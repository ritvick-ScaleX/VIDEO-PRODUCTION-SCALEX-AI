"use client";

import { Sparkles } from "lucide-react";
import { ActivityFeed, describeEvent } from "@/components/dashboard/activity-feed";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { ActivityItem } from "@/lib/types";

const GENERATION_EVENTS = new Set([
  "copy_generated",
  "image_generated",
  "video_generated",
  "ugc_generated",
  "analysis_completed",
  "export_created",
]);

export function RecentGenerations({
  items,
  isLoading,
}: {
  items?: ActivityItem[];
  isLoading?: boolean;
}) {
  const gens = (items ?? [])
    .filter((i) => GENERATION_EVENTS.has(i.event_type))
    .slice(0, 8);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" /> Recent generations
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-10" />
            ))}
          </div>
        ) : gens.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Nothing generated yet — head to the Studio to create your first creative.
          </p>
        ) : (
          <ActivityFeed items={gens} />
        )}
      </CardContent>
    </Card>
  );
}

export default RecentGenerations;
export { describeEvent };
