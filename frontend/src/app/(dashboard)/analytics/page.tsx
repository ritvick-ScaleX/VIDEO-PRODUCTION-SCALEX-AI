"use client";

import { BarChart3 } from "lucide-react";
import { FadeUp } from "@/components/animations/motion";
import { AreaTrend } from "@/components/charts/area-chart";
import { BarBreakdown } from "@/components/charts/bar-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { StatCards } from "@/components/dashboard/stat-cards";
import { ScoreRing } from "@/components/shared/score-ring";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAnalytics } from "@/lib/hooks";
import { titleCase } from "@/lib/utils";

const TREND_KEYS = [
  { key: "products", label: "Products", color: "#4F46E5" },
  { key: "ideas", label: "Ideas", color: "#F59E0B" },
  { key: "images", label: "Images", color: "#22D3EE" },
  { key: "videos", label: "Videos", color: "#C026D3" },
  { key: "exports", label: "Exports", color: "#34D399" },
];

export default function AnalyticsPage() {
  const { data, isLoading } = useAnalytics(30);

  if (isLoading || !data) {
    return (
      <div>
        <PageHeader icon={BarChart3} title="Analytics" description="Growth across your creative studio." />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="mt-6 h-[340px]" />
      </div>
    );
  }

  const platformData = Object.entries(data.platform_breakdown).map(([name, value]) => ({
    name: titleCase(name),
    value,
  }));
  const typeTotals = data.stats
    .filter((s) => ["products", "ideas", "images", "videos"].includes(s.key))
    .map((s) => ({ name: s.label.replace(" Generated", ""), value: s.value }));

  return (
    <div>
      <PageHeader icon={BarChart3} title="Analytics" description="Growth across your creative studio." />

      <StatCards stats={data.stats} />

      <FadeUp delay={0.05} className="mt-6">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Creative output over time</CardTitle>
            <span className="text-xs text-muted-foreground">Last 30 days</span>
          </CardHeader>
          <CardContent>
            <AreaTrend data={data.timeseries} keys={TREND_KEYS} height={320} />
          </CardContent>
        </Card>
      </FadeUp>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <FadeUp delay={0.05}>
          <Card className="h-full">
            <CardHeader><CardTitle>Copy by platform</CardTitle></CardHeader>
            <CardContent>
              {platformData.length ? (
                <DonutChart data={platformData} height={260} />
              ) : (
                <EmptyHint label="Generate copy to see platform mix" />
              )}
            </CardContent>
          </Card>
        </FadeUp>
        <FadeUp delay={0.1}>
          <Card className="h-full">
            <CardHeader><CardTitle>Output by type</CardTitle></CardHeader>
            <CardContent>
              <BarBreakdown data={typeTotals} height={260} />
            </CardContent>
          </Card>
        </FadeUp>
        <FadeUp delay={0.15}>
          <Card className="flex h-full flex-col">
            <CardHeader><CardTitle>Avg creative score</CardTitle></CardHeader>
            <CardContent className="flex flex-1 items-center justify-center">
              <ScoreRing value={data.avg_score} size={150} label="avg" />
            </CardContent>
          </Card>
        </FadeUp>
      </div>

      <FadeUp delay={0.05} className="mt-6">
        <Card>
          <CardHeader><CardTitle>Recent activity</CardTitle></CardHeader>
          <CardContent>
            {data.activity.length ? (
              <ActivityFeed items={data.activity} />
            ) : (
              <EmptyHint label="No activity yet — start generating creatives" />
            )}
          </CardContent>
        </Card>
      </FadeUp>
    </div>
  );
}

function EmptyHint({ label }: { label: string }) {
  return (
    <div className="grid h-[220px] place-items-center rounded-2xl border border-dashed border-border">
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
