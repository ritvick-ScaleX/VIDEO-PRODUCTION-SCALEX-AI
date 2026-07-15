"use client";

import { useId } from "react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";

export interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
}

/**
 * Tiny gradient area sparkline for stat cards. No axes, grid, or tooltip.
 */
export function Sparkline({
  data,
  color = "#6D5EF8",
  height = 48,
}: SparklineProps) {
  const uid = useId().replace(/:/g, "");
  const gradientId = `${uid}-spark`;
  const chartData = data.map((value, index) => ({ index, value }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.4} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
          fillOpacity={1}
          dot={false}
          isAnimationActive
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default Sparkline;
