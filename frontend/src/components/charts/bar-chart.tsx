"use client";

import { useId } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface BarBreakdownProps {
  data: Array<{ name: string; value: number }>;
  color?: string;
  height?: number;
}

const compact = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const tooltipContentStyle: React.CSSProperties = {
  background: "hsl(240 24% 8%)",
  border: "1px solid hsl(240 14% 18%)",
  borderRadius: 12,
  boxShadow: "0 12px 40px -12px rgba(0,0,0,0.6)",
  padding: "10px 12px",
};

/**
 * Single-series bar chart with rounded-top bars and a vertical gradient fill.
 */
export function BarBreakdown({
  data,
  color = "#6D5EF8",
  height = 300,
}: BarBreakdownProps) {
  const uid = useId().replace(/:/g, "");
  const gradientId = `${uid}-bar`;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.95} />
            <stop offset="100%" stopColor={color} stopOpacity={0.35} />
          </linearGradient>
        </defs>

        <CartesianGrid
          vertical={false}
          stroke="hsl(var(--border))"
          strokeOpacity={0.4}
          strokeDasharray="4 4"
        />

        <XAxis
          dataKey="name"
          tickLine={false}
          axisLine={false}
          tickMargin={10}
          interval={0}
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
        />

        <YAxis
          width={40}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(v: number) => compact.format(Number(v))}
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
        />

        <Tooltip
          contentStyle={tooltipContentStyle}
          labelStyle={{
            color: "hsl(var(--muted-foreground))",
            fontSize: 12,
            marginBottom: 4,
          }}
          itemStyle={{ color: "hsl(var(--foreground))", fontSize: 12, padding: 0 }}
          cursor={{ fill: "hsl(var(--border))", fillOpacity: 0.25 }}
        />

        <Bar
          dataKey="value"
          fill={`url(#${gradientId})`}
          radius={[8, 8, 0, 0]}
          maxBarSize={56}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default BarBreakdown;
