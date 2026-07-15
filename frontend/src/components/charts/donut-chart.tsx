"use client";

import {
  Cell,
  Label,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export interface DonutChartProps {
  data: Array<{ name: string; value: number }>;
  height?: number;
}

const AURORA_COLORS = [
  "#6D5EF8",
  "#22D3EE",
  "#C026D3",
  "#34D399",
  "#F59E0B",
  "#F43F5E",
] as const;

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

interface CenterLabelProps {
  viewBox?: { cx?: number; cy?: number };
  total: number;
}

function CenterLabel({ viewBox, total }: CenterLabelProps) {
  const cx = viewBox?.cx ?? 0;
  const cy = viewBox?.cy ?? 0;
  return (
    <g>
      <text
        x={cx}
        y={cy - 4}
        textAnchor="middle"
        dominantBaseline="central"
        fill="hsl(var(--foreground))"
        style={{ fontSize: 22, fontWeight: 600 }}
      >
        {compact.format(total)}
      </text>
      <text
        x={cx}
        y={cy + 18}
        textAnchor="middle"
        dominantBaseline="central"
        fill="hsl(var(--muted-foreground))"
        style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase" }}
      >
        Total
      </text>
    </g>
  );
}

/**
 * Donut (hollow pie) chart cycling the aurora palette, with a dark-glass
 * tooltip, a bottom legend, and the summed total rendered in the center.
 */
export function DonutChart({ data, height = 300 }: DonutChartProps) {
  const total = data.reduce((acc, d) => acc + (Number(d.value) || 0), 0);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Tooltip
          contentStyle={tooltipContentStyle}
          itemStyle={{ color: "hsl(var(--foreground))", fontSize: 12, padding: 0 }}
          labelStyle={{ color: "hsl(var(--muted-foreground))", fontSize: 12 }}
        />

        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius="60%"
          outerRadius="85%"
          paddingAngle={2}
          cornerRadius={4}
          stroke="none"
          isAnimationActive
        >
          {data.map((entry, index) => (
            <Cell
              key={`${entry.name}-${index}`}
              fill={AURORA_COLORS[index % AURORA_COLORS.length]}
            />
          ))}
          <Label content={<CenterLabel total={total} />} position="center" />
        </Pie>

        <Legend
          verticalAlign="bottom"
          iconType="circle"
          iconSize={9}
          formatter={(value: string) => (
            <span style={{ color: "hsl(var(--muted-foreground))", fontSize: 12 }}>
              {value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default DonutChart;
