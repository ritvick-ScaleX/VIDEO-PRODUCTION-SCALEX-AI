"use client";

import { ArrowRight, Boxes, LayoutDashboard, Plus } from "lucide-react";
import Link from "next/link";
import { FadeUp } from "@/components/animations/motion";
import { AreaTrend } from "@/components/charts/area-chart";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentGenerations } from "@/components/dashboard/recent-generations";
import { RecentProducts } from "@/components/dashboard/recent-products";
import { StatCards } from "@/components/dashboard/stat-cards";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveBrand, useAnalytics } from "@/lib/hooks";

const TREND_KEYS = [
  { key: "products", label: "Products", color: "#4F46E5" },
  { key: "ideas", label: "Ideas", color: "#F59E0B" },
  { key: "images", label: "Images", color: "#22D3EE" },
  { key: "videos", label: "Videos", color: "#C026D3" },
];

export default function DashboardPage() {
  const { data, isLoading } = useAnalytics(14);
  const { active } = useActiveBrand();

  return (
    <div>
      <PageHeader
        icon={LayoutDashboard}
        title="Dashboard"
        description={
          active
            ? `Creative command center — ${active.name}`
            : "Your creative command center."
        }
        actions={
          <Button asChild variant="aurora">
            <Link href="/products">
              <Plus className="h-4 w-4" /> New Product
            </Link>
          </Button>
        }
      />

      {isLoading || !data ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <StatCards stats={data.stats} />
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <FadeUp delay={0.05} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>Creative output</CardTitle>
              <span className="text-xs text-muted-foreground">Last 14 days</span>
            </CardHeader>
            <CardContent>
              {isLoading || !data ? (
                <Skeleton className="h-[300px]" />
              ) : (
                <AreaTrend data={data.timeseries} keys={TREND_KEYS} height={300} />
              )}
            </CardContent>
          </Card>
        </FadeUp>
        <FadeUp delay={0.1}>
          <QuickActions />
        </FadeUp>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <FadeUp delay={0.05}>
          <RecentProducts />
        </FadeUp>
        <FadeUp delay={0.1}>
          <RecentGenerations items={data?.activity} isLoading={isLoading} />
        </FadeUp>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <FadeUp delay={0.05}>
          <BrandSummaryCard />
        </FadeUp>
        <FadeUp delay={0.1}>
          <Card>
            <CardHeader>
              <CardTitle>Recent activity</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading || !data ? (
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-10" />
                  ))}
                </div>
              ) : data.activity.length === 0 ? (
                <p className="text-sm text-muted-foreground">No activity yet.</p>
              ) : (
                <ActivityFeed items={data.activity} />
              )}
            </CardContent>
          </Card>
        </FadeUp>
      </div>
    </div>
  );
}

function BrandSummaryCard() {
  const { active } = useActiveBrand();
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Boxes className="h-5 w-5 text-primary" /> Active brand
        </CardTitle>
        <Button asChild variant="ghost" size="sm">
          <Link href="/brands">
            Manage <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {!active ? (
          <p className="text-sm text-muted-foreground">
            No brand yet. Create a brand once and it&apos;s applied to every product and
            generation.
          </p>
        ) : (
          <div className="space-y-4">
            <p className="font-display text-lg font-semibold">{active.name}</p>
            {active.tagline && (
              <p className="text-gradient bg-aurora-line font-display text-base font-semibold">
                “{active.tagline}”
              </p>
            )}
            {active.brand_voice && (
              <p className="line-clamp-2 text-sm text-muted-foreground">
                {active.brand_voice}
              </p>
            )}
            {(active.brand_colors?.length ?? 0) > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                {active.brand_colors.slice(0, 6).map((c) => (
                  <div
                    key={c}
                    className="flex items-center gap-1.5 rounded-full border border-white/10 bg-secondary/50 px-2 py-1"
                  >
                    <span
                      className="h-3.5 w-3.5 rounded-full ring-1 ring-white/20"
                      style={{ background: c }}
                    />
                    <span className="text-[11px] font-medium">{c}</span>
                  </div>
                ))}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              {active.product_count} product{active.product_count === 1 ? "" : "s"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
