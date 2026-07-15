"use client";

import {
  Activity,
  Boxes,
  Download,
  FileText,
  Gauge,
  Image as ImageIcon,
  Lightbulb,
  Package,
  Sparkles,
  Video,
  Wand2,
  type LucideIcon,
} from "lucide-react";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import type { ActivityItem } from "@/lib/types";
import { timeAgo, titleCase } from "@/lib/utils";

interface EventMeta {
  label: string;
  icon: LucideIcon;
  color: string;
}

/** Map a backend event_type string to a friendly label, icon, and color. */
export function describeEvent(eventType: string): EventMeta {
  const e = eventType.toLowerCase();
  const has = (...keys: string[]) => keys.some((k) => e.includes(k));

  if (has("copy")) return { label: "Copy generated", icon: FileText, color: "#6D5EF8" };
  if (has("image")) return { label: "Images generated", icon: ImageIcon, color: "#22D3EE" };
  if (has("video")) return { label: "Video generated", icon: Video, color: "#C026D3" };
  if (has("ugc")) return { label: "UGC script created", icon: Wand2, color: "#34D399" };
  if (has("export")) return { label: "Asset exported", icon: Download, color: "#4F46E5" };
  if (has("score", "scor")) return { label: "Creative scored", icon: Gauge, color: "#22D3EE" };
  if (has("idea")) return { label: "Ideas generated", icon: Lightbulb, color: "#F59E0B" };
  if (has("analy")) return { label: "Product analyzed", icon: Sparkles, color: "#6D5EF8" };
  if (has("brand")) return { label: "Brand added", icon: Boxes, color: "#6D5EF8" };
  if (has("product")) return { label: "Product added", icon: Package, color: "#4F46E5" };
  return { label: titleCase(eventType), icon: Activity, color: "#8A8AA0" };
}

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Activity</CardTitle>
        <CardDescription>Everything happening across your studio</CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <EmptyState
            icon={Activity}
            title="No activity yet"
            description="Your actions across projects will appear here."
          />
        ) : (
          <StaggerGroup className="relative">
            {/* timeline spine */}
            <span
              aria-hidden
              className="absolute bottom-2 left-[15px] top-2 w-px bg-gradient-to-b from-white/[0.12] via-white/[0.06] to-transparent"
            />
            <ol className="space-y-1">
              {items.map((item) => {
                const { label, icon: Icon, color } = describeEvent(item.event_type);
                return (
                  <FadeItem key={item.id}>
                    <li className="relative flex items-start gap-3.5 rounded-2xl py-2 pr-2">
                      <span
                        className="relative z-10 mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full ring-4 ring-background"
                        style={{ backgroundColor: `${color}1f`, color }}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <div className="min-w-0 flex-1 pt-0.5">
                        <p className="truncate text-sm font-medium text-foreground">
                          {label}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {timeAgo(item.created_at)}
                        </p>
                      </div>
                    </li>
                  </FadeItem>
                );
              })}
            </ol>
          </StaggerGroup>
        )}
      </CardContent>
    </Card>
  );
}

export default ActivityFeed;
