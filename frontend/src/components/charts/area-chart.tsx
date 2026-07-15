"use client";

import { useId } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface AreaSeriesKey {
  key: string;
  label: string;
  color: string;
}

export interface AreaTrendProps {
  data: Array<{ date: string; [k: string]: number | string }>;
  keys: AreaSeriesKey[];
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

function formatAxisDate(value: string): string {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/**
 * Multi-series gradient area chart (overlaid). Series colors and labels are
 * passed in; each gets its own vertical fade-to-transparent gradient fill.
 */
export function AreaTrend({ data, keys, height = 300 }: AreaTrendProps) {
  const uid = useId().replace(/:/g, "");

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
        <defs>
          {keys.map((s) => (
            <linearGradient
              key={s.key}
              id={`${uid}-${s.key}`}
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor={s.color} stopOpacity={0.45} />
              <stop offset="100%" stopColor={s.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>

        <CartesianGrid
          vertical={false}
          stroke="hsl(var(--border))"
          strokeOpacity={0.4}
          strokeDasharray="4 4"
        />

        <XAxis
          dataKey="date"
          tickFormatter={formatAxisDate}
          tickLine={false}
          axisLine={false}
          tickMargin={10}
          minTickGap={24}
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
          cursor={{ stroke: "hsl(var(--border))", strokeOpacity: 0.6 }}
          labelFormatter={(label) => formatAxisDate(String(label))}
        />

        {keys.map((s) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.label}
            stroke={s.color}
            strokeWidth={2}
            fill={`url(#${uid}-${s.key})`}
            fillOpacity={1}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default AreaTrend;
