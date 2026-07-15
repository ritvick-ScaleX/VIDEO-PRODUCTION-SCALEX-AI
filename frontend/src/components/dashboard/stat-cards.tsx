"use client";

import {
  Boxes,
  Download,
  FileText,
  Gauge,
  Image as ImageIcon,
  Lightbulb,
  Package,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Video,
  Wand2,
  type LucideIcon,
} from "lucide-react";
import { AnimatedNumber } from "@/components/animations/animated-number";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { Sparkline } from "@/components/charts/sparkline";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { StatCard } from "@/lib/types";

const PALETTE = ["#6D5EF8", "#22D3EE", "#C026D3", "#34D399", "#4F46E5"] as const;

const KEY_META: Record<string, { color: string; icon: LucideIcon }> = {
  brands: { color: "#6D5EF8", icon: Boxes },
  products: { color: "#4F46E5", icon: Package },
  ideas: { color: "#F59E0B", icon: Lightbulb },
  copy: { color: "#6D5EF8", icon: FileText },
  images: { color: "#22D3EE", icon: ImageIcon },
  videos: { color: "#C026D3", icon: Video },
  ugc: { color: "#34D399", icon: Wand2 },
  exports: { color: "#4F46E5", icon: Download },
  scores: { color: "#22D3EE", icon: Gauge },
};

function metaFor(key: string, index: number) {
  return KEY_META[key] ?? { color: PALETTE[index % PALETTE.length], icon: Sparkles };
}

/** Deterministic decorative micro-trend derived from the stat key + delta. */
function seededSeries(seed: string, delta: number, n = 12): number[] {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const rand = () => {
    h = (Math.imul(h, 1664525) + 1013904223) >>> 0;
    return h / 0xffffffff;
  };
  const drift = (delta >= 0 ? 1 : -1) * 0.045;
  const out: number[] = [];
  let v = 0.5;
  for (let i = 0; i < n; i++) {
    v += (rand() - 0.5) * 0.22 + drift;
    out.push(Math.max(0.08, Math.min(1, v)));
  }
  return out;
}

function formatDelta(delta: number): string {
  const rounded = Math.round(Math.abs(delta) * 10) / 10;
  return `${delta >= 0 ? "+" : "-"}${rounded}%`;
}

export function StatCards({ stats }: { stats: StatCard[] }) {
  return (
    <StaggerGroup className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => {
        const { color, icon: Icon } = metaFor(stat.key, i);
        const positive = stat.delta >= 0;
        const series = seededSeries(stat.key, stat.delta);
        return (
          <FadeItem key={stat.key}>
            <div className="group relative overflow-hidden rounded-3xl glass p-5 hover-lift">
              {/* top gradient accent */}
              <div
                aria-hidden
                className="pointer-events-none absolute inset-x-0 top-0 h-px opacity-70"
                style={{
                  background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
                }}
              />
              {/* soft color glow */}
              <div
                aria-hidden
                className="pointer-events-none absolute -right-8 -top-10 h-28 w-28 rounded-full opacity-20 blur-2xl transition-opacity duration-300 group-hover:opacity-40"
                style={{ backgroundColor: color }}
              />

              <div className="flex items-start justify-between gap-3">
                <div
                  className="grid h-10 w-10 place-items-center rounded-xl"
                  style={{ backgroundColor: `${color}1f`, color }}
                >
                  <Icon className="h-5 w-5" />
                </div>
                <Badge
                  variant={positive ? "success" : "destructive"}
                  className="tabular-nums"
                >
                  {positive ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {formatDelta(stat.delta)}
                </Badge>
              </div>

              <p className="mt-4 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {stat.label}
              </p>
              <AnimatedNumber
                value={stat.value}
                format
                className="mt-1 block font-display text-3xl font-bold tracking-tight tabular-nums"
              />

              <div className={cn("mt-3 -mx-1 h-10 opacity-80")}>
                <Sparkline data={series} color={color} height={40} />
              </div>
            </div>
          </FadeItem>
        );
      })}
    </StaggerGroup>
  );
}

export default StatCards;
